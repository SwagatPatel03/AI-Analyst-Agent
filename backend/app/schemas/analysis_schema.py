"""
Analysis schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class AnalysisBase(BaseModel):
    """Base analysis schema"""
    analysis_type: str


class AnalysisCreate(AnalysisBase):
    """Analysis creation schema"""
    report_id: int


class AnalysisResponse(AnalysisBase):
    """Analysis response schema"""
    id: int
    user_id: int
    report_id: int
    status: str
    extracted_data: Optional[Dict[str, Any]] = None
    excel_file_path: Optional[str] = None
    visualizations: Optional[List[str]] = None
    predictions: Optional[Dict[str, Any]] = None
    prediction_accuracy: Optional[float] = None
    report_file_path: Optional[str] = None
    report_summary: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
