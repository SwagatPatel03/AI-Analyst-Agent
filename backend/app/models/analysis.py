from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_type = Column(String)  # visualization, prediction, summary
    visualizations = Column(JSON)  # List of visualization file paths
    ml_predictions = Column(JSON)  # Growth and sales predictions
    generated_report_path = Column(String)
    chat_history = Column(JSON)  # Store chat conversations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    report = relationship("Report", back_populates="analyses")
    user = relationship("User", back_populates="analyses")
