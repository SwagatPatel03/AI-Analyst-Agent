"""
API Routes for Department Lead Extraction and Email
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.services.department_lead_service import DepartmentLeadExtractor
from app.services.department_email_service import DepartmentEmailService
from app.services import auth_service
from app.routes.auth import oauth2_scheme

router = APIRouter(prefix="/api/department-leads", tags=["department-leads"])


class ExtractLeadsRequest(BaseModel):
    report_id: int
    send_email: bool = True


class ExtractLeadsResponse(BaseModel):
    success: bool
    leads: dict
    email_sent: bool = False
    message: str


@router.post("/extract-and-email", response_model=ExtractLeadsResponse)
async def extract_and_email_leads(
    request: ExtractLeadsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Extract department leads from uploaded Excel file and send email
    
    Flow:
    1. Get Report record to find Excel file path
    2. Extract department leads using Groq LLM
    3. Send email to default address (swagatpatel03@gmail.com)
    """
    
    try:
        # Verify token
        current_user = auth_service.get_current_user(db, token)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        # Get report to find Excel file
        from app.models.report import Report
        
        report = db.query(Report).filter(Report.id == request.report_id).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Check if Excel file was generated
        if not report.excel_path:
            raise HTTPException(
                status_code=400, 
                detail="Excel file not generated yet. Please wait for report processing to complete."
            )
        
        if not os.path.exists(report.excel_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Excel file not found at: {report.excel_path}"
            )
        
        # Extract leads from generated Excel
        print(f"🔍 Extracting department leads from generated Excel: {report.excel_path}")
        extractor = DepartmentLeadExtractor()
        leads_data = extractor.extract_leads_from_excel(report.excel_path)
        
        # Send email if requested
        email_sent = False
        if request.send_email:
            print(f"📧 Sending email to: {DepartmentEmailService.DEFAULT_EMAIL}")
            email_service = DepartmentEmailService()
            email_sent = email_service.send_department_leads(
                leads_data=leads_data,
                source_filename=os.path.basename(report.excel_path)
            )
        
        return ExtractLeadsResponse(
            success=True,
            leads=leads_data,
            email_sent=email_sent,
            message=f"Extracted leads for {len(leads_data.get('departments', []))} department(s)"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in extract_and_email_leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview-leads/{report_id}")
async def preview_leads(
    report_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Preview department leads without sending email
    """
    
    request = ExtractLeadsRequest(report_id=report_id, send_email=False)
    return await extract_and_email_leads(request, db, token)


@router.get("/default-email")
async def get_default_email():
    """Get the default email address for department leads"""
    return {
        "email": DepartmentEmailService.DEFAULT_EMAIL,
        "description": "All department lead reports are sent to this email"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    # Check environment variables
    groq_configured = bool(os.getenv('GROQ_API_KEY'))
    sendgrid_configured = bool(os.getenv('SENDGRID_API_KEY'))
    
    return {
        "status": "healthy",
        "groq_configured": groq_configured,
        "sendgrid_configured": sendgrid_configured,
        "default_email": DepartmentEmailService.DEFAULT_EMAIL
    }
