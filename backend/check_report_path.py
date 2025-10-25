"""
Check what's being returned by the report summary endpoint
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Analysis

print("=" * 60)
print("REPORT SUMMARY PATH CHECK")
print("=" * 60)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Get latest summary analysis
analyses = db.query(Analysis).filter(
    Analysis.analysis_type == "summary"
).order_by(Analysis.id.desc()).limit(5).all()

if not analyses:
    print("\n❌ No summary analyses found!")
else:
    for analysis in analyses:
        print(f"\n📄 Analysis ID: {analysis.id}")
        print(f"   Report ID: {analysis.report_id}")
        print(f"   User ID: {analysis.user_id}")
        print(f"   Generated Report Path: {analysis.generated_report_path}")
        
        if analysis.generated_report_path:
            import os
            if os.path.exists(analysis.generated_report_path):
                print(f"   ✅ File exists")
                # Read first 200 chars
                with open(analysis.generated_report_path, 'r', encoding='utf-8') as f:
                    content = f.read(200)
                    print(f"   Preview: {content[:150]}...")
            else:
                print(f"   ❌ File does NOT exist")
        
        if analysis.metadata:
            print(f"   Metadata: {analysis.metadata}")

db.close()
print("\n" + "=" * 60)
