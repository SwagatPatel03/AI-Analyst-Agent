"""
Quick test to verify PDF generation from existing HTML report
"""

from app.services.report_generator import ReportGenerator
import os

# Initialize report generator
report_gen = ReportGenerator()

# Path to existing HTML report
html_path = "outputs/reports/html/report_99999_Microsoft_Corporation.html"

# Test PDF generation
print("🧪 Testing PDF Generation")
print("=" * 80)
print(f"📄 Input HTML: {html_path}")

if not os.path.exists(html_path):
    print(f"❌ HTML file not found: {html_path}")
    exit(1)

print("✅ HTML file exists")

# Generate PDF
try:
    from weasyprint import HTML
    
    pdf_path = "outputs/reports/pdf/report_99999_Microsoft_Corporation.pdf"
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    print(f"🔄 Generating PDF...")
    print(f"📄 Output PDF: {pdf_path}")
    
    HTML(filename=html_path).write_pdf(pdf_path)
    
    print(f"✅ PDF generated successfully!")
    print(f"📊 File size: {os.path.getsize(pdf_path):,} bytes")
    
except ImportError as e:
    print(f"❌ WeasyPrint not available: {e}")
    print("   Install with: pip install weasyprint")

except Exception as e:
    print(f"❌ PDF generation failed: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)
print("✅ Test complete!")
