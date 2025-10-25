"""
Report schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ReportBase(BaseModel):
    """Base report schema"""
    company_name: Optional[str] = None
    report_year: Optional[int] = None


class ReportCreate(ReportBase):
    """Report creation schema"""
    pass


class ReportResponse(ReportBase):
    """Report response schema"""
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
