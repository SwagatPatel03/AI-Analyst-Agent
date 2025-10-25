"""
Report generation routes - ML predictions, report generation, and email
Complete API endpoints for the entire report workflow
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import json
import os
import numpy as np

from app.database import get_db
from app.models.report import Report
from app.models.analysis import Analysis
from app.routes.auth import oauth2_scheme
from app.services import auth_service
from app.services.ml_predictor_enhanced import ml_predictor_enhanced
from app.services.report_generator import report_generator
from app.services.email_service import email_service


def convert_numpy_types(obj):
    """
    Convert numpy types to Python native types for JSON serialization
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    else:
        return obj


router = APIRouter(prefix="/report", tags=["Reports"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class EmailRequest(BaseModel):
    """Email request schema"""
    to_emails: List[EmailStr]
    include_lead_analysis: bool = False


class ReportGenerationRequest(BaseModel):
    """Report generation request schema"""
    generate_pdf: bool = True
    include_visualizations: bool = True



# ============================================================================
# ML PREDICTION ENDPOINTS
# ============================================================================

@router.post("/predict/{report_id}")
async def generate_predictions(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Generate ML predictions for growth and sales
    
    Generates:
    - Growth rate predictions
    - Sales forecast (5 years)
    - Scenario analysis (Best/Base/Worst)
    - Risk assessment
    - Performance metrics
    - Industry comparison
    
    Args:
        report_id: ID of the report
        
    Returns:
        Complete ML predictions dictionary
    """
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Load financial data
    try:
        print(f"\n{'='*80}")
        print(f"🤖 GENERATING PREDICTIONS FOR REPORT {report_id}")
        print(f"{'='*80}")
        
        # NEW: Use ML-ready JSON if available (preferred for predictions)
        if report.ml_data_path and os.path.exists(report.ml_data_path):
            print(f"📂 Loading ML-ready data from: {report.ml_data_path}")
            with open(report.ml_data_path, 'r') as f:
                financial_data = json.load(f)
            print(f"✅ Loaded ML-optimized data")
        else:
            # Fallback: Use extracted data
            print(f"📂 Loading extracted data from: {report.extracted_data_path}")
            with open(report.extracted_data_path, 'r') as f:
                data = json.load(f)
            
            print(f"🔍 Data structure keys: {list(data.keys())}")
            
            # The extracted data IS the financial data (not nested under 'financial_data' key)
            financial_data = data if isinstance(data, dict) and 'company_name' in data else data.get('financial_data', {})
            print(f"⚠️ Using fallback extracted data (ML-ready data not available)")
        
        print(f"\n� FINANCIAL DATA SUMMARY:")
        print(f"  • Company: {financial_data.get('company_name', 'N/A')}")
        print(f"  • Revenue: {financial_data.get('revenue', 'N/A')}")
        print(f"  • Revenue History: {financial_data.get('revenue_history', 'N/A')}")
        print(f"  • Net Income: {financial_data.get('net_income', 'N/A')}")
        print(f"  • Net Income History: {financial_data.get('net_income_history', 'N/A')}")
        print(f"  • Total Assets: {financial_data.get('total_assets', 'N/A')}")
        print(f"  • Key Metrics: {list(financial_data.get('key_metrics', {}).keys()) if financial_data.get('key_metrics') else 'N/A'}")
        
        # Generate predictions using the correct method
        print(f"\n🚀 Calling ML Predictor...")
        predictions = ml_predictor_enhanced.predict_growth_and_sales(
            financial_data,
            report_id,
            scenarios=True,
            include_visualizations=True
        )
        
        print(f"✅ Predictions result: success={predictions.get('success', False)}")
        if not predictions.get('success'):
            print(f"❌ Error: {predictions.get('error', 'Unknown error')}")
        print(f"{'='*80}\n")
        
        # Convert numpy types to Python native types for JSON serialization
        predictions = convert_numpy_types(predictions)
        
        # Save predictions to database
        analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "prediction"
        ).first()
        
        if analysis:
            analysis.ml_predictions = predictions
        else:
            analysis = Analysis(
                report_id=report_id,
                user_id=user.id,
                analysis_type="prediction",
                ml_predictions=predictions
            )
            db.add(analysis)
        
        db.commit()
        db.refresh(analysis)
        
        return {
            "message": "Predictions generated successfully",
            "report_id": report_id,
            "predictions": predictions
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extracted data file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.get("/predictions/{report_id}")
async def get_predictions(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get ML predictions for a report
    
    Returns:
        ML predictions dictionary or empty if not generated yet
    """
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Verify report exists and belongs to user
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get analysis record
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "prediction"
    ).first()
    
    if not analysis or not analysis.ml_predictions:
        # Return empty predictions instead of error
        return {
            "report_id": report_id,
            "analysis_id": None,
            "predictions": None
        }
    
    return {
        "report_id": report_id,
        "analysis_id": analysis.id,
        "predictions": analysis.ml_predictions
    }


# ============================================================================
# REPORT GENERATION ENDPOINTS
# ============================================================================

@router.post("/generate/{report_id}")
async def generate_comprehensive_report(
    report_id: int,
    request: Optional[ReportGenerationRequest] = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive AI-powered report using Gemini
    
    Features:
    - Gemini AI analysis
    - Professional HTML/PDF output
    - Embedded visualizations
    - Executive summary
    - Investment recommendations
    
    Args:
        report_id: ID of the report
        request: Optional generation preferences
        
    Returns:
        Report paths and metadata
    """
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Load financial data
    try:
        with open(report.extracted_data_path, 'r') as f:
            data = json.load(f)
        # Use the full JSON if 'financial_data' key is missing
        if 'financial_data' in data and isinstance(data['financial_data'], dict):
            financial_data = data['financial_data']
        else:
            financial_data = data
        
        # Get predictions (optional)
        prediction_analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "prediction"
        ).first()
        
        predictions = prediction_analysis.ml_predictions if prediction_analysis else {}
        
        # Set defaults
        if request is None:
            request = ReportGenerationRequest()
        
        # Generate report (without visualizations in the report content)
        report_result = report_generator.generate_gemini_report(
            financial_data=financial_data,
            predictions=predictions,
            company_name=report.company_name,
            report_id=report_id,
            visualizations=[],  # Don't include visualizations in report
            generate_pdf=request.generate_pdf
        )
        
        # Save report paths to database
        gen_analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "summary"
        ).first()
        
        new_markdown_path = report_result.get('markdown')
        print(f"DEBUG GENERATE: New markdown path to save: {new_markdown_path}")
        
        if gen_analysis:
            # Store markdown path (we can derive HTML/PDF paths from it)
            old_path = gen_analysis.generated_report_path
            gen_analysis.generated_report_path = new_markdown_path
            print(f"DEBUG GENERATE: Updated existing analysis. Old: {old_path}, New: {gen_analysis.generated_report_path}")
        else:
            gen_analysis = Analysis(
                report_id=report_id,
                user_id=user.id,
                analysis_type="summary",
                generated_report_path=new_markdown_path
            )
            db.add(gen_analysis)
            print(f"DEBUG GENERATE: Created new analysis with path: {new_markdown_path}")
        
        db.commit()
        db.refresh(gen_analysis)
        print(f"DEBUG GENERATE: After commit, DB has: {gen_analysis.generated_report_path}")
        
        return {
            "message": "Report generated successfully",
            "report_id": report_id,
            "company_name": report.company_name,
            "report_paths": {
                "html": report_result.get('html'),
                "markdown": report_result.get('markdown'),
                "pdf": report_result.get('pdf')
            },
            "word_count": report_result.get('word_count'),
            "has_visualizations": False
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extracted data file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation error: {str(e)}"
        )


# ============================================================================
# EMAIL ENDPOINTS
# ============================================================================

@router.post("/email/{report_id}")
async def email_report(
    report_id: int,
    email_request: EmailRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Send report via email with professional HTML template
    
    Features:
    - Professional email template
    - Financial metrics summary
    - Report attachment
    - Optional lead analysis
    
    Args:
        report_id: ID of the report
        email_request: Email configuration
        
    Returns:
        Email sending status
    """
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get generated report
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "summary"
    ).first()
    
    if not analysis or not analysis.generated_report_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated report not found. Generate report first using POST /report/generate/{report_id}"
        )
    
    # Load financial data
    try:
        with open(report.extracted_data_path, 'r') as f:
            data = json.load(f)
        
        financial_data = data.get('financial_data', {})
        
        # Get predictions
        pred_analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "prediction"
        ).first()
        
        predictions = pred_analysis.ml_predictions if pred_analysis else {}
        
        # Send report email
        result = email_service.send_report_email(
            to_emails=email_request.to_emails,
            company_name=report.company_name,
            report_path=analysis.generated_report_path,
            financial_data=financial_data,
            predictions=predictions
        )
        
        # Send lead analysis if requested
        if email_request.include_lead_analysis and result.get('success'):
            lead_analysis = email_service.generate_potential_leads(
                financial_data,
                predictions
            )
            
            lead_result = email_service.send_lead_analysis_email(
                to_emails=email_request.to_emails,
                company_name=report.company_name,
                lead_analysis=lead_analysis
            )
            
            result['lead_analysis_sent'] = lead_result.get('success')
            result['lead_analysis'] = lead_analysis
        
        return result
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report data file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email error: {str(e)}"
        )


@router.post("/leads/{report_id}")
async def generate_leads(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Generate potential leads analysis for investment opportunities
    
    Calculates:
    - Investment score (0-100)
    - Key strengths
    - Risk factors
    - Action items
    - Investment recommendation
    
    Args:
        report_id: ID of the report
        
    Returns:
        Complete lead analysis
    """
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Load financial data
    try:
        with open(report.extracted_data_path, 'r') as f:
            data = json.load(f)
        
        financial_data = data.get('financial_data', {})
        
        # Get predictions
        analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "prediction"
        ).first()
        
        predictions = analysis.ml_predictions if analysis else {}
        
        # Generate lead analysis
        lead_analysis = email_service.generate_potential_leads(
            financial_data, 
            predictions
        )
        
        return {
            "report_id": report_id,
            "company_name": report.company_name,
            "lead_analysis": lead_analysis
        }
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report data file not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lead generation error: {str(e)}"
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/status/{report_id}")
async def get_report_status(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get status of all report components
    
    Returns:
        Status of predictions, visualizations, and generated reports
    """
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check all components
    has_predictions = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "prediction"
    ).first() is not None
    
    has_visualizations = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "visualization"
    ).first() is not None
    
    generated_report = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "summary"
    ).first()
    
    has_report = generated_report is not None and generated_report.generated_report_path is not None
    
    return {
        "report_id": report_id,
        "company_name": report.company_name,
        "status": {
            "has_extracted_data": os.path.exists(report.extracted_data_path) if report.extracted_data_path else False,
            "has_predictions": has_predictions,
            "has_visualizations": has_visualizations,
            "has_generated_report": has_report
        },
        "next_steps": {
            "generate_predictions": not has_predictions,
            "generate_report": has_predictions and not has_report,
            "send_email": has_report
        }
    }

@router.get("/summary/{report_id}")
async def get_report_summary(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get the generated report summary
    
    Returns:
        The Gemini-generated report summary as markdown text
    """
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get the latest generated report analysis (most recent by id)
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "summary"
    ).order_by(Analysis.id.desc()).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report summary not generated yet. Please generate report first."
        )
    
    # Read report content from file
    if analysis.generated_report_path and os.path.exists(analysis.generated_report_path):
        with open(analysis.generated_report_path, 'r', encoding='utf-8') as f:
            report_summary = f.read()
        
        return {
            "report_summary": report_summary,
            "company_name": report.company_name,
            "report_year": report.report_year
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report summary file not found"
        )

@router.get("/pdf/{report_id}")
async def download_report_pdf(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Download the generated report as PDF
    
    Returns:
        PDF file for download
    """
    from fastapi.responses import FileResponse
    
    # Authenticate user
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get generated report analysis
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "summary"
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not generated yet. Please generate report first."
        )
    
    # Derive PDF path from markdown path
    pdf_path = None
    if analysis.generated_report_path:
        # Convert markdown path to PDF path (handle both forward and back slashes)
        import os
        md_path = analysis.generated_report_path
        print(f"DEBUG: Markdown path from DB: {md_path}")
        # Replace the directory part
        md_path = md_path.replace('\\markdown\\', '\\pdf\\').replace('/markdown/', '/pdf/')
        # Replace the extension
        pdf_path = md_path.replace('.md', '.pdf')
        print(f"DEBUG: Derived PDF path: {pdf_path}")
        print(f"DEBUG: PDF exists: {os.path.exists(pdf_path)}")
    
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found. Report may have been generated without PDF."
        )
    
    # Return PDF file
    filename = f"Financial_Report_{report.company_name.replace(' ', '_')}.pdf"
    return FileResponse(
        path=pdf_path,
        media_type='application/pdf',
        filename=filename
    )
