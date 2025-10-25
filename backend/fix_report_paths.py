"""
Fix the stored path to use markdown instead of HTML
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
print("FIXING REPORT PATHS TO USE MARKDOWN")
print("=" * 60)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get all summary analyses
analyses = db.query(Analysis).filter(
    Analysis.analysis_type == "summary"
).all()

if not analyses:
    print("\n❌ No summary analyses found!")
else:
    for analysis in analyses:
        print(f"\n📄 Analysis ID: {analysis.id}")
        print(f"   Current Path: {analysis.generated_report_path}")
        
        if analysis.generated_report_path and '.html' in analysis.generated_report_path:
            # Convert HTML path to Markdown path
            md_path = analysis.generated_report_path.replace('/html/', '/markdown/').replace('.html', '.md')
            
            print(f"   🔄 Converting to: {md_path}")
            
            if os.path.exists(md_path):
                analysis.generated_report_path = md_path
                # Also update metadata
                analysis.metadata = {
                    "html_path": analysis.generated_report_path.replace('/markdown/', '/html/').replace('.md', '.html'),
                    "pdf_path": analysis.generated_report_path.replace('/markdown/', '/pdf/').replace('.md', '.pdf'),
                    "markdown_path": md_path
                }
                print(f"   ✅ Updated to markdown path!")
            else:
                print(f"   ⚠️  Markdown file doesn't exist: {md_path}")
        else:
            print(f"   ✅ Already using markdown or no path set")

db.commit()
db.close()

print("\n" + "=" * 60)
print("✅ All report paths updated!")
print("=" * 60)
