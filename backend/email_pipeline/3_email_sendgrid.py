"""
3. EMAIL - Send emails via SendGrid
Copied from friend's 3_email_sendgrid.py
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


class EmailSender:
    """Simple SendGrid email sender"""
    
    def __init__(self):
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            raise ValueError("SENDGRID_API_KEY environment variable not set")
        
        self.client = SendGridAPIClient(api_key)
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@aianalyst.com')
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: str = None
    ) -> bool:
        """
        Send a single email
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email body
            plain_content: Plain text fallback (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content or self._html_to_text(html_content)
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent to {to_email}")
                return True
            else:
                print(f"❌ Failed to send to {to_email}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to {to_email}: {e}")
            return False
    
    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion"""
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def create_investment_email_html(
    company: str,
    year: int,
    rating: str,
    summary: str,
    opportunities: list,
    risks: list,
    catalysts: list
) -> str:
    """
    Generate professional HTML email for investment leads
    Adapted from friend's email template
    """
    
    # Rating color
    rating_colors = {
        'Strong Buy': '#059669',
        'Buy': '#10b981',
        'Hold': '#eab308',
        'Sell': '#f97316',
        'Strong Sell': '#dc2626'
    }
    rating_color = rating_colors.get(rating, '#6b7280')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .rating-badge {{ display: inline-block; background: {rating_color}; color: white; padding: 8px 20px; border-radius: 20px; margin: 15px 0; font-weight: bold; }}
            .summary {{ background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
            .section {{ margin: 30px 0; }}
            .section-title {{ color: #1f2937; font-size: 20px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
            .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .card-header {{ font-weight: bold; color: #1f2937; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }}
            .badge {{ padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
            .badge-high {{ background: #fee2e2; color: #991b1b; }}
            .badge-medium {{ background: #fef3c7; color: #92400e; }}
            .badge-low {{ background: #e0e7ff; color: #3730a3; }}
            .evidence {{ color: #6b7280; font-size: 14px; line-height: 1.5; }}
            .footer {{ text-align: center; color: #9ca3af; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Investment Analysis: {company}</h1>
            <div>Fiscal Year {year}</div>
            <div class="rating-badge">{rating}</div>
        </div>
        
        <div class="summary">
            <strong>Executive Summary:</strong> {summary}
        </div>
        
        <div class="section">
            <div class="section-title">📈 Investment Opportunities</div>
            {"".join([f'''
            <div class="card">
                <div class="card-header">
                    <span>{opp['title']}</span>
                    <span class="badge badge-{opp.get('potential', 'medium').lower()}">{opp.get('potential', 'Medium')} Potential</span>
                </div>
                <div class="evidence">{opp['evidence']}</div>
                <div style="margin-top: 8px; color: #3b82f6; font-size: 13px;">⏱️ Timeframe: {opp.get('timeframe', 'Medium-term')}</div>
            </div>
            ''' for opp in opportunities])}
        </div>
        
        <div class="section">
            <div class="section-title">⚠️ Risk Factors</div>
            {"".join([f'''
            <div class="card">
                <div class="card-header">
                    <span>{risk['title']}</span>
                    <span class="badge badge-{risk.get('severity', 'medium').lower()}">{risk.get('severity', 'Medium')} Severity</span>
                </div>
                <div class="evidence">{risk['evidence']}</div>
                {f'<div style="margin-top: 8px; color: #059669; font-size: 13px;">💡 Mitigation: {risk.get("mitigation", "")}</div>' if risk.get('mitigation') else ''}
            </div>
            ''' for risk in risks])}
        </div>
        
        <div class="section">
            <div class="section-title">🚀 Growth Catalysts</div>
            {"".join([f'''
            <div class="card">
                <div class="card-header">
                    <span>{catalyst['title']}</span>
                    <span class="badge badge-{catalyst.get('impact', 'medium').lower()}">{catalyst.get('impact', 'Medium')} Impact</span>
                </div>
                <div class="evidence">{catalyst['evidence']}</div>
            </div>
            ''' for catalyst in catalysts])}
        </div>
        
        <div class="footer">
            <p>This analysis was generated by AI Analyst Agent</p>
            <p>For questions or more information, please contact your financial advisor</p>
        </div>
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    # Test email sending
    sender = EmailSender()
    
    test_html = create_investment_email_html(
        company="Test Company",
        year=2024,
        rating="Buy",
        summary="Strong fundamentals with growth potential",
        opportunities=[
            {"title": "Cloud Revenue Growth", "evidence": "30% YoY increase", "potential": "High", "timeframe": "Medium-term"}
        ],
        risks=[
            {"title": "Market Competition", "evidence": "New competitors entering", "severity": "Medium", "mitigation": "Focus on differentiation"}
        ],
        catalysts=[
            {"title": "Product Launch", "evidence": "New product Q2 2024", "impact": "High"}
        ]
    )
    
    print("📧 Test email HTML generated")
    print("To actually send, call: sender.send_email(to_email, subject, html)")
