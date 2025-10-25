"""
Lead Generator Service - Adapted from Friend's Email Pipeline
Converts financial analysis results into investment opportunities and emails stakeholders
"""

import os
import json
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.analysis import Analysis
from app.models.user import User
from app.utils.groq_client import GroqClient
from app.services.email_service import EmailService
from app.config import settings


class LeadGeneratorService:
    """
    Generates investment leads and risk alerts from financial analysis,
    then emails stakeholders. Adapted from friend's department-based system
    to work with financial reports.
    """
    
    def __init__(self):
        self.groq_client = GroqClient()
        self.email_service = EmailService()
    
    def generate_leads_from_report(
        self, 
        db: Session, 
        report_id: int
    ) -> Dict:
        """
        Main orchestrator: Generate investment leads from a completed analysis
        
        Flow:
        1. Load financial data + predictions
        2. LLM analyzes for investment opportunities
        3. Structures as leads (opportunities, risks, catalysts)
        4. Returns structured JSON
        
        Args:
            db: Database session
            report_id: Report ID to generate leads from
            
        Returns:
            Dict with leads, risks, opportunities, next_actions
        """
        # Load report and analysis
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Check if extracted data exists
        if not report.extracted_data_path or not os.path.exists(report.extracted_data_path):
            raise ValueError(f"No extracted data found for report {report_id}. Please run data extraction first.")
        
        # Load extracted data from file
        with open(report.extracted_data_path, 'r') as f:
            extracted_data = json.load(f)
        
        # Get predictions (optional - can work without them)
        analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.analysis_type == "prediction"
        ).first()
        predictions = analysis.ml_predictions if analysis else None
        
        # Prepare evidence text
        evidence = self._prepare_evidence_text(
            report.company_name,
            report.report_year,
            extracted_data,
            predictions
        )
        
        # Call LLM to extract investment leads
        leads_data = self._extract_leads_with_llm(
            company=report.company_name,
            evidence=evidence
        )
        
        return leads_data
    
    def generate_and_email_leads(
        self,
        db: Session,
        report_id: int,
        recipients: List[str],
        preview_only: bool = False
    ) -> Dict:
        """
        Generate leads AND send email to stakeholders
        
        Args:
            db: Database session
            report_id: Report ID
            recipients: List of email addresses
            preview_only: If True, returns HTML without sending
            
        Returns:
            Dict with status, html_preview, leads_data
        """
        # Generate leads
        leads_data = self.generate_leads_from_report(db, report_id)
        
        # Load report details
        report = db.query(Report).filter(Report.id == report_id).first()
        
        # Generate email HTML
        html = self._generate_email_html(
            company=report.company_name,
            year=report.report_year,
            leads_data=leads_data
        )
        
        if preview_only:
            return {
                "status": "preview",
                "html_preview": html,
                "leads_data": leads_data
            }
        
        # Send emails
        subject = f"[Investment Opportunity] {report.company_name} — Analysis Complete"
        
        for recipient in recipients:
            try:
                self.email_service.send_email(
                    to_email=recipient,
                    subject=subject,
                    html_content=html
                )
            except Exception as e:
                print(f"[ERROR] Failed to send to {recipient}: {e}")
        
        return {
            "status": "sent",
            "recipients": recipients,
            "leads_data": leads_data,
            "html_preview": html
        }
    
    def _prepare_evidence_text(
        self,
        company: str,
        year: int,
        extracted_data: Dict,
        predictions: Optional[Dict] = None
    ) -> str:
        """
        Converts extracted_data JSON into readable text for LLM analysis
        Similar to friend's dept_text files, but for financial data
        """
        parts = []
        
        parts.append(f"=== {company} Financial Analysis ({year}) ===\n")
        
        # Financial Performance
        if "revenue" in extracted_data:
            rev = extracted_data["revenue"]
            parts.append(f"\n[Revenue Performance]")
            parts.append(f"Current: ${rev.get('current', 0):,.0f}")
            if "previous" in rev:
                parts.append(f"Previous: ${rev.get('previous', 0):,.0f}")
                growth = ((rev['current'] - rev['previous']) / rev['previous'] * 100) if rev['previous'] else 0
                parts.append(f"Growth: {growth:.1f}%")
        
        if "net_income" in extracted_data:
            ni = extracted_data["net_income"]
            parts.append(f"\n[Net Income]")
            parts.append(f"Current: ${ni.get('current', 0):,.0f}")
            if "previous" in ni:
                parts.append(f"Previous: ${ni.get('previous', 0):,.0f}")
        
        # Key Ratios
        if "key_metrics" in extracted_data:
            metrics = extracted_data["key_metrics"]
            parts.append(f"\n[Key Financial Ratios]")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    parts.append(f"{key}: {value:.2f}")
        
        # Balance Sheet Strength
        if "total_assets" in extracted_data:
            parts.append(f"\n[Balance Sheet]")
            parts.append(f"Total Assets: ${extracted_data['total_assets']:,.0f}")
            if "total_liabilities" in extracted_data:
                parts.append(f"Total Liabilities: ${extracted_data['total_liabilities']:,.0f}")
            if "shareholders_equity" in extracted_data:
                parts.append(f"Shareholders Equity: ${extracted_data['shareholders_equity']:,.0f}")
        
        # Predictions
        if predictions:
            parts.append(f"\n[ML Predictions]")
            if "growth_rate" in predictions:
                parts.append(f"Predicted Growth Rate: {predictions['growth_rate'].get('predicted', 0):.1f}%")
            if "investment_score" in predictions:
                parts.append(f"Investment Score: {predictions.get('investment_score', 0)}/100")
            if "risk_metrics" in predictions:
                risk = predictions["risk_metrics"]
                parts.append(f"Volatility: {risk.get('volatility', 0):.1f}%")
                parts.append(f"Risk Rating: {risk.get('risk_rating', 'Unknown')}")
        
        # Segments
        if "segments" in extracted_data:
            parts.append(f"\n[Business Segments]")
            for seg in extracted_data["segments"]:
                parts.append(f"- {seg.get('name', 'Unknown')}: ${seg.get('revenue', 0):,.0f}")
        
        # Management Insights
        if "management_insights" in extracted_data:
            insights = extracted_data["management_insights"]
            if "business_strategy" in insights:
                parts.append(f"\n[Management Strategy]")
                parts.append(insights["business_strategy"][:500])  # Cap at 500 chars
        
        # Limit total length to avoid context overflow
        full_text = "\n".join(parts)
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "\n... (truncated)"
        
        return full_text
    
    def _extract_leads_with_llm(self, company: str, evidence: str) -> Dict:
        """
        Calls Groq LLM to extract investment leads from financial evidence
        Adapted from friend's 2_llm.py
        
        Returns structured JSON with:
        - opportunities: Investment opportunities (like friend's "leads")
        - risks: Financial and business risks
        - catalysts: Growth catalysts (like friend's "next_actions")
        - summary: Executive summary
        - rating: Buy/Hold/Sell recommendation
        """
        system_prompt = """You are a professional investment analyst. Analyze the financial evidence and return JSON:
{
  "company": "<string>",
  "summary": "<2-3 sentence executive summary>",
  "rating": "<Strong Buy|Buy|Hold|Sell|Strong Sell>",
  "opportunities": [
    {
      "title": "<opportunity title>",
      "evidence": "<specific data supporting this>",
      "potential": "<High|Medium|Low>",
      "timeframe": "<Short-term|Medium-term|Long-term>"
    }
  ],
  "risks": [
    {
      "title": "<risk title>",
      "severity": "<High|Medium|Low>",
      "evidence": "<specific data>",
      "mitigation": "<how to mitigate>"
    }
  ],
  "catalysts": [
    {
      "title": "<growth catalyst>",
      "impact": "<High|Medium|Low>",
      "evidence": "<supporting data>"
    }
  ],
  "key_metrics": {
    "investment_score": 0-100,
    "confidence": "<High|Medium|Low>"
  }
}

Base everything on the provided financial data. If data is missing, mark as "Unknown" or leave empty.
"""
        
        user_prompt = f"""Company: {company}

Financial Evidence:
---
{evidence}
---

Return JSON only with investment analysis.
"""
        
        # Call Groq API (chat_completion only takes messages and optional context)
        response = self.groq_client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Response is already a string (the content), not a dict
        # Robust JSON extraction (from friend's code)
        json_text = self._extract_first_json_block(response)
        leads_data = json.loads(json_text)
        
        return leads_data
    
    def _extract_first_json_block(self, text: str) -> str:
        """
        Robustly extract JSON from LLM response
        Copied from friend's 2_llm.py
        """
        import re
        
        # Try bracket slice first
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1 and e > s:
            candidate = text[s:e+1]
            try:
                json.loads(candidate)
                return candidate
            except Exception:
                pass
        
        # Fallback: regex
        matches = list(re.finditer(r"\{.*\}", text, flags=re.DOTALL))
        for m in reversed(matches):
            chunk = m.group(0)
            try:
                json.loads(chunk)
                return chunk
            except Exception:
                continue
        
        raise ValueError("No valid JSON object found in LLM response")
    
    def _generate_email_html(
        self,
        company: str,
        year: int,
        leads_data: Dict
    ) -> str:
        """
        Generates HTML email from leads data
        Adapted from friend's EMAIL_TEMPLATE
        """
        opportunities = leads_data.get("opportunities", [])
        risks = leads_data.get("risks", [])
        catalysts = leads_data.get("catalysts", [])
        summary = leads_data.get("summary", "No summary available")
        rating = leads_data.get("rating", "Hold")
        key_metrics = leads_data.get("key_metrics", {})
        
        # Build opportunities HTML
        opp_html = ""
        if opportunities:
            for opp in opportunities:
                opp_html += f"""
                <li>
                    <b>{opp.get('title', 'Untitled')}</b> — 
                    <span style="color:#10b981">[{opp.get('potential', 'Unknown')} Potential]</span>
                    <br><i>Evidence:</i> {opp.get('evidence', 'N/A')}
                    <br><i>Timeframe:</i> {opp.get('timeframe', 'Unknown')}
                </li>
                """
        else:
            opp_html = "<li>No opportunities identified</li>"
        
        # Build risks HTML
        risk_html = ""
        if risks:
            for risk in risks:
                severity_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}.get(risk.get("severity", "Medium"), "#6b7280")
                risk_html += f"""
                <li>
                    <b>{risk.get('title', 'Untitled')}</b> — 
                    <span style="color:{severity_color}">[{risk.get('severity', 'Unknown')} Severity]</span>
                    <br><i>Evidence:</i> {risk.get('evidence', 'N/A')}
                    <br><i>Mitigation:</i> {risk.get('mitigation', 'N/A')}
                </li>
                """
        else:
            risk_html = "<li>No significant risks identified</li>"
        
        # Build catalysts HTML
        catalyst_html = ""
        if catalysts:
            for cat in catalysts:
                catalyst_html += f"""
                <li>
                    <b>{cat.get('title', 'Untitled')}</b> — 
                    <span style="color:#8b5cf6">[{cat.get('impact', 'Unknown')} Impact]</span>
                    <br><i>Evidence:</i> {cat.get('evidence', 'N/A')}
                </li>
                """
        else:
            catalyst_html = "<li>No growth catalysts identified</li>"
        
        # Rating color
        rating_colors = {
            "Strong Buy": "#10b981",
            "Buy": "#34d399",
            "Hold": "#f59e0b",
            "Sell": "#f87171",
            "Strong Sell": "#ef4444"
        }
        rating_color = rating_colors.get(rating, "#6b7280")
        
        # Build complete email
        html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: system-ui, -apple-system, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h2 {{
            color: #8b5cf6;
            border-bottom: 2px solid #8b5cf6;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #6b7280;
            margin-top: 24px;
        }}
        .rating-box {{
            background: #f3f4f6;
            border-left: 4px solid {rating_color};
            padding: 12px 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .metric {{
            display: inline-block;
            margin-right: 20px;
            font-weight: 600;
        }}
        ul {{
            list-style: none;
            padding-left: 0;
        }}
        li {{
            margin-bottom: 16px;
            padding: 12px;
            background: #f9fafb;
            border-radius: 6px;
            border-left: 3px solid #e5e7eb;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h2>🎯 Investment Analysis: {company} (FY{year})</h2>
    
    <div class="rating-box">
        <span class="metric">Recommendation:</span> 
        <span style="color:{rating_color}; font-size:18px; font-weight:bold;">{rating}</span>
        <br>
        <span class="metric">Investment Score:</span> {key_metrics.get('investment_score', 'N/A')}/100
        <br>
        <span class="metric">Confidence:</span> {key_metrics.get('confidence', 'Unknown')}
    </div>
    
    <h3>📊 Executive Summary</h3>
    <p>{summary}</p>
    
    <h3>💡 Investment Opportunities</h3>
    <ul>{opp_html}</ul>
    
    <h3>⚠️ Risk Factors</h3>
    <ul>{risk_html}</ul>
    
    <h3>🚀 Growth Catalysts</h3>
    <ul>{catalyst_html}</ul>
    
    <div class="footer">
        <p>
            <b>Generated automatically by AI Analyst Agent</b><br>
            This analysis is based on financial data and ML predictions. 
            Not financial advice. Please conduct your own due diligence.
        </p>
    </div>
</body>
</html>
"""
        
        return html


# Convenience function for easy import
def generate_leads_and_email(
    db: Session,
    report_id: int,
    recipients: List[str],
    preview_only: bool = False
) -> Dict:
    """
    Convenience function to generate leads and send emails
    """
    service = LeadGeneratorService()
    return service.generate_and_email_leads(db, report_id, recipients, preview_only)
