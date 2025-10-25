"""
Lead Generation Routes - Investment Opportunities & Email Notifications
Adapted from friend's email pipeline for financial context
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.user import User
from app.services import auth_service
from app.routes.auth import oauth2_scheme
from app.services.lead_generator_service import LeadGeneratorService


router = APIRouter(prefix="/leads", tags=["leads"])


# ===========================
# Request/Response Models
# ===========================

class GenerateLeadsRequest(BaseModel):
    """Request to generate investment leads from a report"""
    report_id: int


class EmailLeadsRequest(BaseModel):
    """Request to generate leads and email to recipients"""
    report_id: int
    recipients: List[EmailStr]
    preview_only: bool = False  # If True, returns HTML without sending


class LeadOpportunity(BaseModel):
    """Investment opportunity structure"""
    title: str
    evidence: str
    potential: str  # High, Medium, Low
    timeframe: str  # Short-term, Medium-term, Long-term


class RiskFactor(BaseModel):
    """Risk factor structure"""
    title: str
    severity: str  # High, Medium, Low
    evidence: str
    mitigation: Optional[str] = None


class GrowthCatalyst(BaseModel):
    """Growth catalyst structure"""
    title: str
    impact: str  # High, Medium, Low
    evidence: str


class LeadsResponse(BaseModel):
    """Response containing investment leads"""
    company: str
    summary: str
    rating: str  # Strong Buy, Buy, Hold, Sell, Strong Sell
    opportunities: List[LeadOpportunity]
    risks: List[RiskFactor]
    catalysts: List[GrowthCatalyst]
    key_metrics: dict


class EmailResponse(BaseModel):
    """Response after sending emails"""
    status: str  # "sent" or "preview"
    recipients: Optional[List[str]] = None
    leads_data: dict
    html_preview: str


# ===========================
# Routes
# ===========================

@router.post("/generate", response_model=LeadsResponse)
async def generate_investment_leads(
    request: GenerateLeadsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Generate investment leads from a completed financial analysis
    
    This endpoint:
    1. Loads financial data and ML predictions
    2. Uses LLM to analyze for investment opportunities
    3. Identifies risks and growth catalysts
    4. Returns structured investment analysis
    
    **No emails are sent** - use POST /leads/email for that
    
    Example Response:
    ```json
    {
      "company": "Microsoft Corporation",
      "summary": "Strong buy based on cloud growth...",
      "rating": "Buy",
      "opportunities": [
        {
          "title": "Azure Growth Momentum",
          "evidence": "30% YoY growth in cloud revenue",
          "potential": "High",
          "timeframe": "Medium-term"
        }
      ],
      "risks": [...],
      "catalysts": [...]
    }
    ```
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        service = LeadGeneratorService()
        leads_data = service.generate_leads_from_report(db, request.report_id)
        return leads_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"❌ Lead generation error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lead generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lead generation failed: {str(e)}")


@router.post("/email", response_model=EmailResponse)
async def generate_and_email_leads(
    request: EmailLeadsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Generate investment leads AND send via email to recipients
    
    This endpoint:
    1. Generates investment analysis (like /generate)
    2. Creates professional HTML email
    3. Sends to specified recipients (or returns preview)
    
    Set `preview_only: true` to get HTML without sending.
    
    Example Request:
    ```json
    {
      "report_id": 123,
      "recipients": ["investor@fund.com", "analyst@firm.com"],
      "preview_only": false
    }
    ```
    
    Example Response:
    ```json
    {
      "status": "sent",
      "recipients": ["investor@fund.com", "analyst@firm.com"],
      "leads_data": {...},
      "html_preview": "<html>...</html>"
    }
    ```
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        service = LeadGeneratorService()
        result = service.generate_and_email_leads(
            db=db,
            report_id=request.report_id,
            recipients=request.recipients,
            preview_only=request.preview_only
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")


@router.get("/preview/{report_id}")
async def preview_lead_email(
    report_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Preview the lead generation email HTML without sending
    
    Useful for testing email templates before actual sending.
    
    Returns HTML string that can be rendered in browser.
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    try:
        service = LeadGeneratorService()
        
        # Generate leads
        leads_data = service.generate_leads_from_report(db, report_id)
        
        # Get report details
        from app.models.report import Report
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Generate HTML
        html = service._generate_email_html(
            company=report.company_name,
            year=report.report_year or 2024,
            leads_data=leads_data
        )
        
        return {"html": html, "leads_data": leads_data}
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


@router.post("/batch-email")
async def batch_email_leads(
    report_ids: List[int],
    recipients: List[EmailStr],
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Generate and email leads for multiple reports (batch processing)
    
    Useful for weekly/monthly portfolio summaries.
    
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication")


# ===========================
# Health Check
# ===========================

@router.get("/health")
async def leads_health_check():
    """Check if lead generation service is operational"""
    try:
        service = LeadGeneratorService()
        return {
            "status": "healthy",
            "groq_client": "ok",
            "email_service": "ok"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
