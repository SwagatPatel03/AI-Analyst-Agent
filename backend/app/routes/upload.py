"""
File upload routes with complete processing pipeline
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models.report import Report
from app.models.user import User
from app.routes.auth import oauth2_scheme
from app.services import auth_service
from app.services.data_extractor import data_extractor
from app.services.data_validator import data_validator
from app.services.excel_generator_v2 import excel_generator_v2
from app.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/json", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/excel", exist_ok=True)

@router.post("/report")
async def upload_report(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    report_year: Optional[int] = Form(None),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Upload and process annual report"""
    
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed size"
        )
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create database record
    report = Report(
        user_id=user.id,
        company_name=company_name,
        report_year=report_year,
        filename=file.filename,
        file_path=file_path,
        file_type=file_ext,
        status="processing"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    try:
        # Process PDF and extract data
        print(f"\n🚀 Starting processing for report ID: {report.id}")
        print(f"📊 Company: {company_name}, File: {file.filename}")
        
        extracted_data = data_extractor.extract_from_pdf(file_path, company_name)
        
        # Validate and clean data
        print("🔍 Validating and cleaning data...")
        financial_data = extracted_data['financial_data']
        cleaned_data = data_validator.validate_and_clean(financial_data)
        print("✅ Data validated and cleaned")
        
        # Save main JSON
        json_path = f"{OUTPUT_DIR}/json/{unique_id}.json"
        print(f"💾 Saving JSON to: {json_path}")
        data_extractor.save_extracted_data(cleaned_data, json_path)
        print(f"✅ JSON saved successfully")
        
        # Save ML-ready JSON (NEW: For ML predictions)
        ml_ready_data = extracted_data.get('ml_ready_data', {})
        if ml_ready_data:
            ml_json_path = data_extractor.save_ml_ready_data(ml_ready_data, json_path)
            print(f"✅ ML-ready JSON saved successfully")
        else:
            print(f"⚠️ No ML-ready data found in extraction")
            ml_json_path = None
        
        # Generate Excel
        excel_path = f"{OUTPUT_DIR}/excel/{unique_id}.xlsx"
        print(f"📊 Generating Excel file: {excel_path}")
        excel_generator_v2.generate_excel(cleaned_data, excel_path)
        print(f"✅ Excel generated successfully")
        
        # Update database record
        print("💾 Updating database...")
        report.extracted_data_path = json_path
        report.ml_data_path = ml_json_path  # NEW: Save ML-ready JSON path
        report.excel_path = excel_path
        report.status = "completed"
        db.commit()
        print(f"✅ Report processing completed! ID: {report.id}\n")
        
        return {
            "message": "Report processed successfully",
            "report_id": report.id,
            "company_name": company_name,
            "json_path": json_path,
            "excel_path": excel_path,
            "status": "completed"
        }
        
    except Exception as e:
        # Update status to failed
        report.status = "failed"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing report: {str(e)}"
        )

@router.get("/reports")
async def get_user_reports(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all reports for authenticated user"""
    
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    reports = db.query(Report).filter(Report.user_id == user.id).all()
    
    return {
        "reports": [
            {
                "id": r.id,
                "company_name": r.company_name,
                "report_year": r.report_year,
                "filename": r.filename,
                "status": r.status,
                "created_at": r.created_at
            }
            for r in reports
        ]
    }

@router.get("/report/{report_id}")
async def get_report(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get specific report details"""
    
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return {
        "id": report.id,
        "company_name": report.company_name,
        "report_year": report.report_year,
        "filename": report.filename,
        "status": report.status,
        "json_path": report.extracted_data_path,
        "excel_path": report.excel_path,
        "created_at": report.created_at
    }

@router.delete("/report/{report_id}")
async def delete_report(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Delete a report and associated files"""
    
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete files
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)
    
    if report.extracted_data_path and os.path.exists(report.extracted_data_path):
        os.remove(report.extracted_data_path)
    
    if report.excel_path and os.path.exists(report.excel_path):
        os.remove(report.excel_path)
    
    # Delete database record
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}
