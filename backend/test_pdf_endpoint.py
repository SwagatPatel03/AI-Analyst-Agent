"""
Test PDF download endpoint logic
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis
import os

print("=" * 60)
print("PDF DOWNLOAD ENDPOINT TEST")
print("=" * 60)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get latest summary analysis
analysis = db.query(Analysis).filter(
    Analysis.analysis_type == "summary"
).order_by(Analysis.id.desc()).first()

if analysis:
    print(f"\n✅ Found analysis: ID {analysis.id}")
    print(f"   Report ID: {analysis.report_id}")
    print(f"   Markdown Path: {analysis.generated_report_path}")
    
    # Derive PDF path (same logic as endpoint)
    pdf_path = None
    if analysis.generated_report_path:
        pdf_path = analysis.generated_report_path.replace('/markdown/', '/pdf/').replace('.md', '.pdf')
        print(f"   Derived PDF Path: {pdf_path}")
        
        if os.path.exists(pdf_path):
            print(f"\n✅ PDF file EXISTS and is accessible!")
            print(f"   File size: {os.path.getsize(pdf_path)} bytes")
            print(f"\n🎉 PDF download endpoint should work now!")
        else:
            print(f"\n❌ PDF file NOT FOUND at: {pdf_path}")
    else:
        print(f"\n❌ No generated_report_path in analysis")
else:
    print("\n❌ No summary analysis found")

db.close()
print("\n" + "=" * 60)
