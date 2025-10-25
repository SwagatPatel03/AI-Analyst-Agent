"""
Check if PDF file exists and find its path
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis
import os
import glob

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

analysis = db.query(Analysis).filter(
    Analysis.analysis_type == "summary"
).order_by(Analysis.id.desc()).first()

if analysis:
    print(f"Analysis ID: {analysis.id}")
    print(f"Report ID: {analysis.report_id}")
    print(f"Generated Path: {analysis.generated_report_path}")
    
    # If we have markdown path, derive PDF path
    if analysis.generated_report_path and '.md' in analysis.generated_report_path:
        pdf_path = analysis.generated_report_path.replace('/markdown/', '/pdf/').replace('.md', '.pdf')
        print(f"\nDerived PDF path: {pdf_path}")
        
        if os.path.exists(pdf_path):
            print(f"✅ PDF file EXISTS!")
            print(f"   Size: {os.path.getsize(pdf_path)} bytes")
        else:
            print(f"❌ PDF file does NOT exist")
            
            # Check what PDF files exist
            pdf_dir = "outputs/reports/pdf"
            if os.path.exists(pdf_dir):
                pdfs = glob.glob(f"{pdf_dir}/*.pdf")
                print(f"\nAvailable PDFs in {pdf_dir}:")
                for pdf in pdfs:
                    print(f"  - {pdf}")
            else:
                print(f"\n❌ PDF directory doesn't exist: {pdf_dir}")

db.close()
