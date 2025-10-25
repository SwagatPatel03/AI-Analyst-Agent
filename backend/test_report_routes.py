"""
Complete Report Routes Test
Tests all 6 report endpoints sequentially

Prerequisites:
1. pip install pydantic-settings sendgrid sqlalchemy
2. Add SENDGRID_API_KEY to .env
3. Upload a document to get report_id
4. Get auth token
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_AUTH_TOKEN_HERE"  # Replace with actual token
REPORT_ID = 1  # Replace with actual report_id
EMAIL = "your-email@example.com"  # Replace with your email

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def print_test_header(step, title):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"STEP {step}: {title}")
    print("="*80)

def print_response(response):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-"*80)

def test_complete_workflow():
    """Test complete report generation workflow"""
    
    print("\n🚀 STARTING COMPLETE REPORT ROUTES TEST")
    print(f"Report ID: {REPORT_ID}")
    print(f"Time: {datetime.now()}")
    
    # Step 1: Generate Predictions
    print_test_header(1, "Generate ML Predictions")
    response = requests.post(
        f"{BASE_URL}/report/predict/{REPORT_ID}",
        headers=headers
    )
    print_response(response)
    
    if response.status_code != 200:
        print("❌ Failed to generate predictions. Stopping test.")
        return
    
    predictions = response.json().get('predictions', {})
    print(f"✅ Predictions generated successfully")
    print(f"   - Growth Rate: {predictions.get('growth_rate', 'N/A')}")
    print(f"   - Risk Score: {predictions.get('risk_assessment', {}).get('overall_risk_score', 'N/A')}")
    
    # Step 2: Get Predictions
    print_test_header(2, "Retrieve Saved Predictions")
    response = requests.get(
        f"{BASE_URL}/report/predictions/{REPORT_ID}",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        print("✅ Predictions retrieved successfully")
    else:
        print("⚠️  Could not retrieve predictions")
    
    # Step 3: Check Status
    print_test_header(3, "Check Report Status")
    response = requests.get(
        f"{BASE_URL}/report/status/{REPORT_ID}",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        status = response.json().get('status', {})
        print("✅ Status retrieved:")
        print(f"   - Has Data: {status.get('has_extracted_data', False)}")
        print(f"   - Has Predictions: {status.get('has_predictions', False)}")
        print(f"   - Has Visualizations: {status.get('has_visualizations', False)}")
        print(f"   - Has Report: {status.get('has_generated_report', False)}")
    
    # Step 4: Generate Report
    print_test_header(4, "Generate Comprehensive Report")
    response = requests.post(
        f"{BASE_URL}/report/generate/{REPORT_ID}",
        headers=headers,
        json={
            "generate_pdf": True,
            "include_visualizations": True
        }
    )
    print_response(response)
    
    if response.status_code != 200:
        print("❌ Failed to generate report. Stopping test.")
        return
    
    report_data = response.json()
    print(f"✅ Report generated successfully")
    print(f"   - HTML: {report_data.get('report_paths', {}).get('html', 'N/A')}")
    print(f"   - PDF: {report_data.get('report_paths', {}).get('pdf', 'N/A')}")
    print(f"   - Word Count: {report_data.get('word_count', 'N/A')}")
    
    # Step 5: Generate Lead Analysis
    print_test_header(5, "Generate Lead Analysis")
    response = requests.post(
        f"{BASE_URL}/report/leads/{REPORT_ID}",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        lead_data = response.json().get('lead_analysis', {})
        print(f"✅ Lead analysis generated:")
        print(f"   - Investment Score: {lead_data.get('investment_score', 'N/A')}/100")
        print(f"   - Recommendation: {lead_data.get('recommendation', 'N/A')}")
        print(f"   - Strengths: {len(lead_data.get('strengths', []))}")
        print(f"   - Risks: {len(lead_data.get('risks', []))}")
        print(f"   - Actions: {len(lead_data.get('action_items', []))}")
    else:
        print("⚠️  Could not generate lead analysis")
    
    # Step 6: Send Email (Optional - only if you want to test email)
    print_test_header(6, "Send Report via Email (OPTIONAL)")
    send_email = input(f"Send email to {EMAIL}? (y/n): ").lower().strip()
    
    if send_email == 'y':
        response = requests.post(
            f"{BASE_URL}/report/email/{REPORT_ID}",
            headers=headers,
            json={
                "to_emails": [EMAIL],
                "include_lead_analysis": True
            }
        )
        print_response(response)
        
        if response.status_code == 200:
            print(f"✅ Email sent successfully to {EMAIL}")
            print("   - Check your inbox for:")
            print("     1. Financial Report Email")
            print("     2. Investment Opportunity Email (Lead Analysis)")
        else:
            print("❌ Failed to send email")
    else:
        print("⏭️  Skipping email test")
    
    # Final Status Check
    print_test_header(7, "Final Status Check")
    response = requests.get(
        f"{BASE_URL}/report/status/{REPORT_ID}",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        status = response.json().get('status', {})
        next_steps = response.json().get('next_steps', {})
        
        print("\n📊 FINAL STATUS:")
        print(f"   ✅ Extracted Data: {status.get('has_extracted_data', False)}")
        print(f"   ✅ Predictions: {status.get('has_predictions', False)}")
        print(f"   ✅ Visualizations: {status.get('has_visualizations', False)}")
        print(f"   ✅ Generated Report: {status.get('has_generated_report', False)}")
        
        print("\n🎯 NEXT STEPS:")
        for step, needed in next_steps.items():
            status_icon = "📋" if needed else "✅"
            print(f"   {status_icon} {step}: {'Needed' if needed else 'Complete'}")
    
    print("\n" + "="*80)
    print("✅ COMPLETE REPORT ROUTES TEST FINISHED")
    print("="*80)

def test_individual_endpoints():
    """Test individual endpoints for debugging"""
    print("\n🔧 INDIVIDUAL ENDPOINT TESTS")
    
    tests = [
        ("POST", f"/report/predict/{REPORT_ID}", None),
        ("GET", f"/report/predictions/{REPORT_ID}", None),
        ("POST", f"/report/generate/{REPORT_ID}", {"generate_pdf": True}),
        ("POST", f"/report/leads/{REPORT_ID}", None),
        ("GET", f"/report/status/{REPORT_ID}", None),
    ]
    
    for method, endpoint, data in tests:
        print(f"\n{method} {endpoint}")
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        print("-"*40)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REPORT ROUTES COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Check configuration
    if TOKEN == "YOUR_AUTH_TOKEN_HERE":
        print("\n❌ ERROR: Please set TOKEN variable")
        print("   Get token from: POST /auth/login")
        exit(1)
    
    if EMAIL == "your-email@example.com":
        print("\n⚠️  WARNING: Using default email address")
        print("   Update EMAIL variable to receive test emails")
    
    print(f"\nConfiguration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Report ID: {REPORT_ID}")
    print(f"  Email: {EMAIL}")
    
    choice = input("\nSelect test:\n1. Complete Workflow\n2. Individual Endpoints\n\nChoice (1/2): ").strip()
    
    if choice == "1":
        test_complete_workflow()
    elif choice == "2":
        test_individual_endpoints()
    else:
        print("Invalid choice")
