from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String, nullable=False)
    report_year = Column(Integer)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    extracted_data_path = Column(String)  # Path to JSON file
    ml_data_path = Column(String)  # Path to ML-ready JSON file (NEW)
    excel_path = Column(String)  # Path to generated Excel
    status = Column(String, default="uploaded")  # uploaded, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="reports")
    analyses = relationship("Analysis", back_populates="report")
