"""
Check metadata field properly
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis
import json

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

analysis = db.query(Analysis).filter(
    Analysis.analysis_type == "summary"
).order_by(Analysis.id.desc()).first()

if analysis:
    print(f"Analysis ID: {analysis.id}")
    print(f"Generated Path: {analysis.generated_report_path}")
    print(f"Metadata type: {type(analysis.metadata)}")
    print(f"Metadata value: {analysis.metadata}")
    
    # Try to access as dict
    if hasattr(analysis.metadata, 'get'):
        print(f"\nHTML path: {analysis.metadata.get('html_path')}")
        print(f"PDF path: {analysis.metadata.get('pdf_path')}")
        print(f"Markdown path: {analysis.metadata.get('markdown_path')}")

db.close()
