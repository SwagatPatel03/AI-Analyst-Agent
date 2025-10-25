"""
Email Service for Department Leads
Sends department-wise lead reports to concerned members
"""

import os
from typing import Dict, List
import requests


class DepartmentEmailService:
    """Send department lead reports via email"""
    
    # Default email for all department leads (as per requirement)
    DEFAULT_EMAIL = "swagatpatel03@gmail.com"
    
    def __init__(self):
        # Get API key from environment or config
        from app.config import settings
        
        # Try Mailgun first, then SendGrid
        self.mailgun_api_key = settings.MAILGUN_API_KEY if settings.MAILGUN_API_KEY != "not-configured" else None
        self.mailgun_domain = settings.MAILGUN_DOMAIN if settings.MAILGUN_DOMAIN != "not-configured" else None
        self.sendgrid_api_key = settings.SENDGRID_API_KEY if settings.SENDGRID_API_KEY != "not-configured" else None
        
        self.from_email = settings.FROM_EMAIL
        
        # Determine which service to use
        if self.mailgun_api_key and self.mailgun_domain:
            self.email_service = 'mailgun'
            print(f"🔧 DepartmentEmailService initialized with Mailgun")
        elif self.sendgrid_api_key:
            self.email_service = 'sendgrid'
            print(f"🔧 DepartmentEmailService initialized with SendGrid")
        else:
            self.email_service = None
            print(f"⚠️  No email service configured (Mailgun or SendGrid)")
        
        print(f"   From Email: {self.from_email}")
    
    def send_department_leads(self, leads_data: Dict, source_filename: str = "uploaded_file.xlsx") -> bool:
        """
        Send department leads email
        
        Args:
            leads_data: Dictionary with department leads (from DepartmentLeadExtractor)
            source_filename: Name of the Excel file analyzed
            
        Returns:
            True if email sent successfully, False otherwise
        """
        
        # Generate HTML content
        html_content = self._create_email_html(leads_data, source_filename)
        
        # Create email subject
        dept_count = len(leads_data.get('departments', []))
        subject = f"Department Leads Report - {dept_count} Department(s) Analyzed"
        
        # Send email
        return self._send_email(
            to_email=self.DEFAULT_EMAIL,
            subject=subject,
            html_content=html_content
        )
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via Mailgun or SendGrid"""
        
        if not self.email_service:
            raise ValueError("No email service configured. Set MAILGUN_API_KEY/MAILGUN_DOMAIN or SENDGRID_API_KEY")
        
        if self.email_service == 'mailgun':
            return self._send_via_mailgun(to_email, subject, html_content)
        else:
            return self._send_via_sendgrid(to_email, subject, html_content)
    
    def _send_via_mailgun(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via Mailgun API"""
        
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"AI Analyst <{self.from_email}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Email sent successfully via Mailgun!")
                print(f"   To: {to_email}")
                print(f"   Message ID: {response.json().get('id')}")
                return True
            else:
                print(f"❌ Mailgun error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Mailgun sending failed: {e}")
            return False
    
    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SendGrid (fallback)"""
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            print(f"✅ Email sent successfully via SendGrid!")
            print(f"   To: {to_email}")
            print(f"   Status: {response.status_code}")
            
            return response.status_code in [200, 202]
            
        except Exception as e:
            print(f"❌ SendGrid sending failed: {e}")
            return False
    
    def _create_email_html(self, leads_data: Dict, source_filename: str) -> str:
        """Create professional HTML email template"""
        
        departments = leads_data.get('departments', [])
        summary = leads_data.get('summary', 'No summary available')
        
        # Build department sections
        dept_sections = ""
        for dept in departments:
            dept_sections += self._create_department_section(dept)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Department Leads Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .summary {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}
        .summary h2 {{
            margin-top: 0;
            color: #667eea;
        }}
        .department {{
            margin-bottom: 30px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .dept-header {{
            background: #667eea;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .dept-header h3 {{
            margin: 0;
            font-size: 20px;
        }}
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        .status-growing {{
            background: #28a745;
        }}
        .status-stable {{
            background: #ffc107;
            color: #333;
        }}
        .status-declining {{
            background: #dc3545;
        }}
        .dept-body {{
            padding: 20px;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .section h4 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        .section p {{
            margin: 5px 0;
            line-height: 1.8;
        }}
        .work-items {{
            list-style: none;
            padding: 0;
        }}
        .work-items li {{
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }}
        .work-items li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }}
        .concerns {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 15px;
            border-radius: 5px;
        }}
        .concerns h4 {{
            color: #856404;
            margin-top: 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
        .source-file {{
            background: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-family: monospace;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Department Leads Report</h1>
        <p>Growth Analysis & Status Updates</p>
    </div>
    
    <div class="content">
        <div class="source-file">
            <strong>Source File:</strong> {source_filename}
        </div>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>{summary}</p>
        </div>
        
        {dept_sections}
    </div>
    
    <div class="footer">
        <p>This is an automated report generated by AI Analyst Agent</p>
        <p>If you have questions, please contact your system administrator</p>
    </div>
</body>
</html>
"""
        return html
    
    def _create_department_section(self, dept: Dict) -> str:
        """Create HTML section for a single department"""
        
        name = dept.get('name', 'Unknown Department')
        growth = dept.get('growth', 'No growth data available')
        status = dept.get('status', 'stable')
        work_items = dept.get('work_items', [])
        concerns = dept.get('concerns', '')
        
        # Status badge class
        status_class = f"status-{status.lower()}"
        
        # Work items HTML
        work_items_html = ""
        if work_items:
            work_items_html = "<ul class='work-items'>"
            for item in work_items:
                work_items_html += f"<li>{item}</li>"
            work_items_html += "</ul>"
        else:
            work_items_html = "<p>No specific work items identified</p>"
        
        # Concerns HTML
        concerns_html = ""
        if concerns and concerns.strip():
            concerns_html = f"""
            <div class="concerns">
                <h4>⚠️ Concerns & Risks</h4>
                <p>{concerns}</p>
            </div>
            """
        
        return f"""
        <div class="department">
            <div class="dept-header">
                <h3>{name}</h3>
                <span class="status-badge {status_class}">{status.upper()}</span>
            </div>
            <div class="dept-body">
                <div class="section">
                    <h4>📈 Growth Indicators</h4>
                    <p>{growth}</p>
                </div>
                
                <div class="section">
                    <h4>✓ Key Work Items</h4>
                    {work_items_html}
                </div>
                
                {concerns_html}
            </div>
        </div>
        """


# Test function
def test_email():
    """Test email sending with sample data"""
    
    sample_leads = {
        "departments": [
            {
                "name": "Sales",
                "growth": "20% increase in Q4 revenue",
                "status": "growing",
                "work_items": [
                    "New client acquisition campaign",
                    "Expanded into APAC market"
                ],
                "concerns": "Need more sales staff to handle demand"
            },
            {
                "name": "Engineering",
                "growth": "15% productivity improvement",
                "status": "stable",
                "work_items": [
                    "Completed V2.0 release",
                    "Migrated to cloud infrastructure"
                ],
                "concerns": ""
            }
        ],
        "summary": "Overall positive growth across departments with strong sales performance"
    }
    
    # Uncomment to test (requires SENDGRID_API_KEY)
    # service = DepartmentEmailService()
    # service.send_department_leads(sample_leads, "test_file.xlsx")
    
    print("DepartmentEmailService ready!")


if __name__ == "__main__":
    test_email()
