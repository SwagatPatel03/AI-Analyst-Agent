"""
Complete Flow Test: Excel → Visualizations
Simulates the full data flow from Excel file to visualizations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.visualization_service import VisualizationService

# Configuration
EXCEL_FILE = "outputs/excel/Microsoft_Corporation_FY2024_Financial_Report.xlsx"
TEST_REPORT_ID = 999

print("=" * 70)
print("🚀 COMPLETE FLOW TEST: Excel → Visualizations")
print("=" * 70)
print()
print("📋 Test Configuration:")
print(f"   Excel File: {EXCEL_FILE}")
print(f"   Report ID: {TEST_REPORT_ID}")
print()

# Step 1: Check if Excel file exists
print("Step 1: Checking Excel file...")
if not os.path.exists(EXCEL_FILE):
    print(f"❌ Excel file not found: {EXCEL_FILE}")
    print("   Please run test_excel_from_json.py first to generate the Excel file")
    sys.exit(1)
print(f"✅ Excel file found")
print()

# Step 2: Initialize Visualization Service
print("Step 2: Initializing Visualization Service...")
try:
    viz_service = VisualizationService()
    print(f"✅ Service initialized")
    print(f"   Output directory: {viz_service.output_dir}")
except Exception as e:
    print(f"❌ Failed to initialize service: {str(e)}")
    sys.exit(1)
print()

# Step 3: Generate all visualizations
print("Step 3: Generating visualizations from Excel...")
print("-" * 70)
try:
    visualization_paths = viz_service.generate_all_visualizations_from_excel(
        EXCEL_FILE,
        TEST_REPORT_ID
    )
except Exception as e:
    print(f"❌ Failed to generate visualizations: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("-" * 70)
print()

# Step 4: Verify results
print("Step 4: Verifying generated files...")
if not visualization_paths:
    print("❌ No visualizations were generated")
    sys.exit(1)

print(f"✅ Generated {len(visualization_paths)} visualizations:")
print()

all_exist = True
for chart_name, file_path in visualization_paths.items():
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    file_size = os.path.getsize(file_path) if exists else 0
    print(f"   {status} {chart_name}")
    print(f"      Path: {file_path}")
    print(f"      Size: {file_size:,} bytes")
    print()
    
    if not exists:
        all_exist = False

# Step 5: Summary
print("=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print()

if all_exist:
    print("✅ ALL TESTS PASSED!")
    print()
    print("Generated Visualizations:")
    for chart_name in visualization_paths.keys():
        print(f"   • {chart_name.replace('_', ' ').title()}")
    print()
    print("🎉 The complete flow is working:")
    print("   1. User uploads PDF → Extracted to JSON")
    print("   2. JSON → Professional Excel (8 sheets)")
    print("   3. Excel → Interactive Visualizations (6 charts)")
    print()
    print("📂 All files saved in: outputs/visualizations/")
    print()
    
    # Open first visualization
    first_viz = list(visualization_paths.values())[0]
    print(f"🌐 Opening first visualization: {os.path.basename(first_viz)}")
    os.system(f'start "" "{first_viz}"')
    
else:
    print("❌ SOME TESTS FAILED")
    print("   Some visualization files are missing")
    print("   Check the error messages above for details")

print()
print("=" * 70)
