"""
Email Service for sending reports and lead analysis via SendGrid
Supports: Report emails, Lead analysis, Investment opportunities
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from typing import List, Dict, Any, Optional
import base64
import os
from app.config import settings


class EmailService:
    """Service for sending emails via SendGrid with professional templates"""
    
    def __init__(self):
        """Initialize SendGrid client"""
        try:
            self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.from_email = settings.FROM_EMAIL
        except Exception as e:
            print(f"⚠️  SendGrid initialization failed: {e}")
            self.sg = None
            self.from_email = "noreply@ai-analyst.com"
    
    def send_report_email(
        self,
        to_emails: List[str],
        company_name: str,
        report_path: str,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send financial report via email with professional HTML template
        
        Args:
            to_emails: List of recipient emails
            company_name: Company name
            report_path: Path to report file (HTML/PDF)
            financial_data: Financial data summary
            predictions: ML predictions
        
        Returns:
            Status of email sending
        """
        if not self.sg:
            return {
                "success": False,
                "error": "SendGrid not configured",
                "message": "Email service unavailable"
            }
        
        # Generate email content
        subject = f"Financial Analysis Report - {company_name}"
        html_content = self._generate_email_html(
            company_name,
            financial_data,
            predictions
        )
        
        # Create message
        message = Mail(
            from_email=self.from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=html_content
        )
        
        # Attach report if exists
        if report_path and os.path.exists(report_path):
            with open(report_path, 'rb') as f:
                file_data = f.read()
            
            encoded_file = base64.b64encode(file_data).decode()
            
            # Determine file type
            file_ext = os.path.splitext(report_path)[1].lower()
            file_type = 'text/html' if file_ext == '.html' else 'application/pdf'
            
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(os.path.basename(report_path)),
                FileType(file_type),
                Disposition('attachment')
            )
            message.attachment = attached_file
        
        try:
            response = self.sg.send(message)
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Email sent successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send email"
            }
    
    def send_lead_analysis_email(
        self,
        to_emails: List[str],
        company_name: str,
        lead_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send lead analysis and follow-up recommendations
        
        Args:
            to_emails: List of recipient emails
            company_name: Company name
            lead_analysis: Lead analysis with investment score
        
        Returns:
            Status of email sending
        """
        if not self.sg:
            return {
                "success": False,
                "error": "SendGrid not configured"
            }
        
        subject = f"Investment Opportunity Analysis - {company_name}"
        html_content = self._generate_lead_email_html(company_name, lead_analysis)
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=html_content
        )
        
        try:
            response = self.sg.send(message)
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Lead analysis email sent successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Legacy method for backward compatibility
    @staticmethod
    async def send_report(to_email: str, report_path: str, company_name: str):
        """
        Legacy method - kept for backward compatibility
        Now redirects to new send_report_email method
        
        Args:
            to_email: Recipient email address
            report_path: Path to report file
            company_name: Name of the company
        """
        service = EmailService()
        return service.send_report_email(
            to_emails=[to_email],
            company_name=company_name,
            report_path=report_path,
            financial_data={"company_name": company_name},
            predictions={}
        )
    
    def _generate_email_html(
        self,
        company_name: str,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> str:
        """Generate HTML email template for report"""
        
        # Extract revenue (handle different formats)
        revenue_current = financial_data.get('revenue', 0)
        revenue_previous = 0
        if 'revenue_history' in financial_data and financial_data['revenue_history']:
            revenue_previous = financial_data['revenue_history'][0] if len(financial_data['revenue_history']) > 0 else 0
        
        # Extract growth predictions
        growth_rate = predictions.get('growth_rate', 0)
        confidence_interval = predictions.get('confidence_interval', {})
        
        # Extract recommendations
        recommendations = predictions.get('recommendations', [])
        if isinstance(recommendations, dict):
            recommendations = [f"{r.get('type', '')}: {r.get('recommendation', '')}" 
                             for r in recommendations.values() if isinstance(r, dict)]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .metric {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #667eea;
        }}
        .highlight {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .recommendation {{
            background: white;
            padding: 10px 15px;
            margin: 5px 0;
            border-left: 3px solid #28a745;
            border-radius: 3px;
        }}
        .footer {{
            text-align: center;
            color: #666;
            padding: 20px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Financial Analysis Report</h1>
            <p>{company_name}</p>
        </div>
        <div class="content">
            <h2>Executive Summary</h2>
            
            <div class="metric">
                <div class="metric-label">Current Revenue</div>
                <div>${revenue_current:,.0f} USD</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">Previous Revenue</div>
                <div>${revenue_previous:,.0f} USD</div>
            </div>
            
            <div class="highlight">
                <h3>Growth Prediction</h3>
                <p><strong>Predicted Growth Rate:</strong> {growth_rate:.2f}%</p>
                <p><strong>Confidence Interval:</strong> {confidence_interval.get('lower', 0):.2f}% to {confidence_interval.get('upper', 0):.2f}%</p>
            </div>
            
            <h3>Key Recommendations</h3>
            {self._format_recommendations_html(recommendations)}
            
            <p style="margin-top: 30px;">
                <strong>Note:</strong> The complete detailed report is attached to this email.
                Please review it for comprehensive analysis and insights.
            </p>
        </div>
        <div class="footer">
            <p>This is an automated email from AI Analyst Agent</p>
            <p>© 2025 AI Analyst Agent. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_lead_email_html(
        self,
        company_name: str,
        lead_analysis: Dict[str, Any]
    ) -> str:
        """Generate HTML email for lead analysis"""
        
        investment_score = lead_analysis.get('investment_score', 0)
        key_strengths = lead_analysis.get('key_strengths', [])
        risk_factors = lead_analysis.get('risk_factors', [])
        action_items = lead_analysis.get('action_items', [])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .content {{
            background: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
        }}
        .strength {{
            color: #28a745;
            padding: 8px;
            margin: 5px 0;
        }}
        .risk {{
            color: #dc3545;
            padding: 8px;
            margin: 5px 0;
        }}
        .action {{
            background: #e3f2fd;
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #2196f3;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Investment Opportunity</h1>
            <p>{company_name}</p>
            <div class="score">Score: {investment_score}/100</div>
        </div>
        <div class="content">
            <div class="section">
                <h2>Key Strengths</h2>
                {self._format_list_html(key_strengths, 'strength')}
            </div>
            
            <div class="section">
                <h2>Risk Factors</h2>
                {self._format_list_html(risk_factors, 'risk')}
            </div>
            
            <div class="section">
                <h2>Recommended Actions</h2>
                {self._format_list_html(action_items, 'action')}
            </div>
            
            <p style="margin-top: 30px; text-align: center;">
                <strong>Follow up with the investment team to discuss this opportunity.</strong>
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _format_recommendations_html(self, recommendations: List[str]) -> str:
        """Format recommendations as HTML"""
        if not recommendations:
            return "<p>No specific recommendations available.</p>"
        
        html = ""
        for rec in recommendations:
            html += f'<div class="recommendation">• {rec}</div>'
        
        return html
    
    def _format_list_html(self, items: List[str], class_name: str) -> str:
        """Format list items as HTML"""
        if not items:
            return "<p>None identified.</p>"
        
        html = ""
        for item in items:
            html += f'<div class="{class_name}">• {item}</div>'
        
        return html
    
    def generate_potential_leads(
        self,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate lead analysis for investment opportunities
        
        Args:
            financial_data: Company financial data
            predictions: ML predictions
        
        Returns:
            Lead analysis with investment score and recommendations
        """
        
        # Extract metrics (handle different formats)
        metrics = financial_data.get('key_metrics', {})
        growth_rate = predictions.get('growth_rate', 0)
        
        # Calculate investment score (0-100)
        score = 50  # Base score
        
        # Growth impact
        if growth_rate > 15:
            score += 20
        elif growth_rate > 10:
            score += 15
        elif growth_rate > 5:
            score += 10
        elif growth_rate < 0:
            score -= 15
        
        # ROE impact
        roe = metrics.get('roe', 0)
        if roe and roe > 20:
            score += 15
        elif roe and roe > 15:
            score += 10
        elif roe and roe < 5:
            score -= 10
        
        # Debt impact
        debt_ratio = metrics.get('debt_to_equity', 0)
        if debt_ratio and debt_ratio < 0.5:
            score += 10
        elif debt_ratio and debt_ratio > 1.5:
            score -= 10
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Identify strengths
        strengths = []
        if growth_rate > 10:
            strengths.append(f"Strong growth trajectory: {growth_rate:.1f}% predicted")
        if roe and roe > 15:
            strengths.append(f"Excellent ROE: {roe:.1f}%")
        if debt_ratio and debt_ratio < 0.5:
            strengths.append(f"Conservative debt levels: {debt_ratio:.2f}")
        
        # Identify risks
        risks = []
        if growth_rate < 0:
            risks.append("Negative growth predicted")
        if roe and roe < 5:
            risks.append("Low return on equity")
        if debt_ratio and debt_ratio > 1.5:
            risks.append("High debt-to-equity ratio")
        
        # Action items
        actions = []
        if score > 70:
            actions.append("Schedule meeting with investment team")
            actions.append("Request detailed due diligence")
            actions.append("Prepare investment proposal")
        elif score > 50:
            actions.append("Monitor quarterly performance")
            actions.append("Request additional financial data")
        else:
            actions.append("Flag for re-evaluation in next quarter")
            actions.append("Identify specific improvement areas")
        
        return {
            "investment_score": score,
            "key_strengths": strengths,
            "risk_factors": risks,
            "action_items": actions,
            "recommendation": self._get_investment_recommendation(score)
        }
    
    def _get_investment_recommendation(self, score: int) -> str:
        """Get investment recommendation based on score"""
        if score >= 80:
            return "Strong Buy - Excellent investment opportunity"
        elif score >= 70:
            return "Buy - Good investment with solid fundamentals"
        elif score >= 60:
            return "Hold - Monitor closely for improvement"
        elif score >= 50:
            return "Cautious - Requires deeper analysis"
        else:
            return "Avoid - High risk, low potential"


# Singleton instance for easy import
email_service = EmailService()

