"""
Analysis routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List
import json
import os

from app.database import get_db
from app.services import auth_service
from app.routes.auth import oauth2_scheme
from app.services.data_extractor import DataExtractor
from app.services.excel_generator_v2 import ExcelGeneratorV2
from app.services.visualization_service import VisualizationService
from app.services.ml_predictor_enhanced import ml_predictor_enhanced
from app.schemas.analysis_schema import AnalysisResponse, AnalysisCreate
from app.models.user import User
from app.models.report import Report
from app.models.analysis import Analysis

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/extract/{report_id}", response_model=AnalysisResponse)
async def extract_data(
    report_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Extract financial data from a report
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        report_id=report_id,
        analysis_type="extraction"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Add background task for data extraction
    background_tasks.add_task(
        DataExtractor.process_report,
        report.file_path,
        analysis.id,
        db
    )
    
    return analysis


@router.post("/visualize/{analysis_id}", response_model=AnalysisResponse)
async def generate_visualizations(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Generate visualizations from extracted data
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if not analysis.extracted_data:
        raise HTTPException(status_code=400, detail="No extracted data available")
    
    # Add background task for visualization
    background_tasks.add_task(
        VisualizationService.generate_charts,
        analysis.extracted_data,
        analysis.id,
        db
    )
    
    return analysis


@router.post("/predict/{analysis_id}", response_model=AnalysisResponse)
async def predict_growth(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Generate ML predictions for growth/sales
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if not analysis.extracted_data:
        raise HTTPException(status_code=400, detail="No extracted data available")
    
    # Add background task for enhanced prediction
    from app.services.ml_predictor_enhanced import predict_metrics
    background_tasks.add_task(
        predict_metrics,
        analysis.extracted_data,
        analysis.id,
        db
    )
    
    return analysis


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get analysis by ID
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis


@router.get("/report/{report_id}", response_model=List[AnalysisResponse])
async def list_analyses(
    report_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    List all analyses for a report
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    analyses = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == current_user.id
    ).all()
    
    return analyses


# ==================== NEW VISUALIZATION ENDPOINTS ====================

# Internal helper function (defined first)
async def generate_report_visualizations_internal(
    report_id: int,
    token: str,
    db: Session
):
    """
    Internal function: Generate all visualizations for a report (uses new VisualizationService)
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
    
    if report.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report processing not completed"
        )
    
    # Check if Excel file exists
    if not report.excel_path or not os.path.exists(report.excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found. Please ensure the report has been processed."
        )
    
    try:
        # Generate visualizations from Excel file
        from app.services.visualization_service import VisualizationService
        viz_service = VisualizationService()
        visualization_paths = viz_service.generate_all_visualizations_from_excel(
            report.excel_path, 
            report_id
        )
        
        # Convert dict to list of paths (frontend expects array)
        viz_list = list(visualization_paths.values()) if isinstance(visualization_paths, dict) else visualization_paths
        
        # Create or update analysis record
        analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "visualization"
        ).first()
        
        if analysis:
            # Update existing analysis
            analysis.visualizations = viz_list
        else:
            # Create new analysis
            analysis = Analysis(
                report_id=report_id,
                user_id=user.id,
                analysis_type="visualization",
                visualizations=viz_list
            )
            db.add(analysis)
        
        db.commit()
        db.refresh(analysis)
        
        return {
            "message": "Visualizations generated successfully",
            "analysis_id": analysis.id,
            "visualization_count": len(viz_list),
            "visualizations": viz_list
        }
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating visualizations: {str(e)}"
        )


# Public route endpoint (uses internal function)
@router.post("/visualize/report/{report_id}")
async def generate_visualizations_by_report(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Generate all visualizations for a report (primary endpoint for frontend)
    """
    return await generate_report_visualizations_internal(report_id, token, db)


@router.get("/visualizations/{report_id}")
async def get_report_visualizations(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get all visualizations for a report
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
        Analysis.analysis_type == "visualization"
    ).first()
    
    if not analysis or not analysis.visualizations:
        # Return empty list instead of error - let frontend handle generation
        return {
            "report_id": report_id,
            "analysis_id": None,
            "visualizations": []
        }
    
    # Validate that files actually exist on disk
    valid_visualizations = []
    for viz_path in analysis.visualizations:
        if os.path.exists(viz_path):
            valid_visualizations.append(viz_path)
        else:
            print(f"⚠️ Visualization file not found: {viz_path}")
    
    # If no valid files exist, return empty list (frontend will show generate button)
    if not valid_visualizations:
        print(f"⚠️ No valid visualization files found for report {report_id}")
        return {
            "report_id": report_id,
            "analysis_id": analysis.id,
            "visualizations": []
        }
    
    # Update database if some files were missing (clean up invalid paths)
    if len(valid_visualizations) < len(analysis.visualizations):
        print(f"🧹 Cleaning up {len(analysis.visualizations) - len(valid_visualizations)} invalid paths from database")
        analysis.visualizations = valid_visualizations
        db.commit()
    
    return {
        "report_id": report_id,
        "analysis_id": analysis.id,
        "visualizations": valid_visualizations
    }


@router.get("/visualization/file")
async def serve_visualization_file(
    file_path: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Serve a specific visualization HTML file
    """
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Security: ensure file path is within outputs directory
    normalized_path = os.path.normpath(file_path)
    if not normalized_path.startswith("outputs\\visualizations") and not normalized_path.startswith("outputs/visualizations"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Invalid file path"
        )
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visualization file not found"
        )
    
    return FileResponse(
        file_path,
        media_type="text/html",
        filename=os.path.basename(file_path)
    )


@router.get("/excel/{report_id}")
async def download_excel_report(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Download generated Excel file for a report
    """
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
    
    if not report.excel_path or not os.path.exists(report.excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found"
        )
    
    return FileResponse(
        report.excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{report.company_name}_financial_data.xlsx"
    )


# ============================================================================
# CUSTOM VISUALIZATION ENDPOINTS - Let users create their own charts!
# ============================================================================

@router.get("/excel-structure/{report_id}")
async def get_excel_data_structure(
    report_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get available data structure from Excel file for custom visualization builder
    
    Returns sheets, columns, and preview data so user can choose what to visualize
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
    
    if not report.excel_path or not os.path.exists(report.excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found. Generate visualizations first."
        )
    
    try:
        from app.services.custom_visualization_service import custom_viz_service
        structure = custom_viz_service.get_excel_data_structure(report.excel_path)
        return structure
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read Excel structure: {str(e)}"
        )


@router.post("/custom-visualization/{report_id}")
async def create_custom_visualization(
    report_id: int,
    chart_config: dict,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Create a custom visualization based on user configuration
    
    Request body example:
    {
        "sheet_name": "Income Statement",
        "chart_type": "bar",  // bar, line, pie, scatter, area
        "x_column": "Metric",
        "y_columns": ["2023", "2024"],
        "title": "Revenue Comparison",
        "filter": {"column": "Metric", "contains": "Revenue"}  // optional
    }
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
    
    if not report.excel_path or not os.path.exists(report.excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found. Generate visualizations first."
        )
    
    try:
        from app.services.custom_visualization_service import custom_viz_service
        chart_path = custom_viz_service.create_custom_chart(
            report.excel_path,
            report_id,
            chart_config
        )
        
        # Get or create custom visualization analysis record
        analysis = db.query(Analysis).filter(
            Analysis.report_id == report_id,
            Analysis.user_id == user.id,
            Analysis.analysis_type == "custom_visualization"
        ).first()
        
        if analysis:
            # Add new chart to existing list
            # Important: Create a new list to trigger SQLAlchemy change detection
            custom_charts = list(analysis.visualizations or [])
            custom_charts.append(chart_path)
            analysis.visualizations = custom_charts
            # Explicitly mark the field as modified for PostgreSQL
            flag_modified(analysis, 'visualizations')
            print(f"✅ Added custom chart to existing analysis. Total charts: {len(custom_charts)}")
        else:
            # Create new analysis record for custom charts
            analysis = Analysis(
                report_id=report_id,
                user_id=user.id,
                analysis_type="custom_visualization",
                visualizations=[chart_path]
            )
            db.add(analysis)
            print(f"✅ Created new custom visualization analysis record")
        
        db.commit()
        db.refresh(analysis)
        
        return {
            "success": True,
            "chart_path": chart_path,
            "all_custom_charts": analysis.visualizations,
            "message": "Custom visualization created successfully!"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create visualization: {str(e)}"
        )


@router.get("/custom-visualizations/{report_id}")
async def get_custom_visualizations(
    report_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get all custom visualizations created by user for a report
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
    
    # Get custom visualizations
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "custom_visualization"
    ).first()
    
    return {
        "custom_visualizations": analysis.visualizations if analysis else [],
        "count": len(analysis.visualizations) if analysis and analysis.visualizations else 0
    }

