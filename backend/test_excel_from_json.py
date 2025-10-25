"""
Test script to generate Excel from existing JSON file using V2 generator
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.excel_generator_v2 import excel_generator_v2
import json

# Read existing JSON
json_file = "outputs/json/c0f206fd-5221-4b1a-88ca-78156f42fa80.json"

print(f"📖 Reading JSON file: {json_file}")
with open(json_file, 'r', encoding='utf-8') as f:
    financial_data = json.load(f)

print(f"✅ Loaded JSON data")
print(f"   Keys: {list(financial_data.keys())}")

# Generate Excel
company_name = financial_data.get('metadata', {}).get('company_name', 'Company')
fiscal_year = financial_data.get('metadata', {}).get('fiscal_year', '2024')
output_file = f"outputs/excel/{company_name.replace(' ', '_')}_FY{fiscal_year}_Financial_Report.xlsx"

print(f"\n📊 Generating comprehensive Excel report...")
print(f"   Company: {company_name}")
print(f"   Fiscal Year: {fiscal_year}")

excel_path = excel_generator_v2.generate_excel(financial_data, output_file)

print(f"\n✅ Excel file created successfully!")
print(f"   Location: {excel_path}")
print(f"\n📂 Opening file in Excel...")

# Open the file
os.system(f'start "" "{excel_path}"')
