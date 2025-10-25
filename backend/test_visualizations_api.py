"""
Test script for visualization API endpoints
Tests the new visualization routes added to /api/analysis
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_visualization_endpoints():
    print("\n" + "="*60)
    print("🎨 Testing Visualization API Endpoints")
    print("="*60)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPass123!"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    print(f"✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get user's reports
    print("\n2️⃣ Getting user reports...")
    response = requests.get(
        f"{BASE_URL}/api/upload/reports",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get reports: {response.status_code}")
        return
    
    reports = response.json().get("reports", [])
    if not reports:
        print("⚠️ No reports found. Upload a report first using test_pipeline.py")
        return
    
    # Get the most recent completed report
    completed_report = None
    for report in reports:
        if report.get("status") == "completed":
            completed_report = report
            break
    
    if not completed_report:
        print("⚠️ No completed reports found. Complete an upload first.")
        return
    
    report_id = completed_report["id"]
    print(f"✅ Found completed report: ID={report_id}, Company={completed_report['company_name']}")
    
    # Step 3: Generate visualizations
    print(f"\n3️⃣ Generating visualizations for report {report_id}...")
    response = requests.post(
        f"{BASE_URL}/api/analysis/visualize/report/{report_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to generate visualizations: {response.status_code}")
        print(response.text)
        return
    
    viz_data = response.json()
    print(f"✅ Visualizations generated successfully!")
    print(f"   Analysis ID: {viz_data['analysis_id']}")
    print(f"   Visualization count: {viz_data['visualization_count']}")
    print(f"\n   Generated charts:")
    for chart_name, path in viz_data['visualizations'].items():
        print(f"   • {chart_name}: {path}")
    
    # Step 4: Retrieve visualizations
    print(f"\n4️⃣ Retrieving visualizations for report {report_id}...")
    response = requests.get(
        f"{BASE_URL}/api/analysis/visualizations/{report_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to retrieve visualizations: {response.status_code}")
        print(response.text)
        return
    
    viz_list = response.json()
    print(f"✅ Retrieved visualizations:")
    print(f"   Report ID: {viz_list['report_id']}")
    print(f"   Analysis ID: {viz_list['analysis_id']}")
    print(f"   Charts available: {len(viz_list['visualizations'])}")
    
    # Step 5: Test downloading Excel
    print(f"\n5️⃣ Testing Excel download for report {report_id}...")
    response = requests.get(
        f"{BASE_URL}/api/analysis/excel/{report_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to download Excel: {response.status_code}")
    else:
        print(f"✅ Excel download successful!")
        print(f"   File size: {len(response.content):,} bytes")
        print(f"   Content-Type: {response.headers.get('content-type')}")
    
    # Step 6: Test serving a visualization file
    if viz_data['visualizations']:
        print(f"\n6️⃣ Testing visualization file serving...")
        # Get first visualization path
        first_viz_name = list(viz_data['visualizations'].keys())[0]
        first_viz_path = viz_data['visualizations'][first_viz_name]
        
        response = requests.get(
            f"{BASE_URL}/api/analysis/visualization/file",
            params={"file_path": first_viz_path},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to serve visualization file: {response.status_code}")
            print(response.text)
        else:
            print(f"✅ Visualization file served successfully!")
            print(f"   File: {first_viz_name}")
            print(f"   Size: {len(response.content):,} bytes")
            print(f"   Content-Type: {response.headers.get('content-type')}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ All visualization API tests completed!")
    print("="*60)
    print("\n📊 Available endpoints:")
    print(f"   POST /api/analysis/visualize/report/{{report_id}} - Generate visualizations")
    print(f"   GET  /api/analysis/visualizations/{{report_id}}     - Get visualization list")
    print(f"   GET  /api/analysis/visualization/file               - Serve visualization HTML")
    print(f"   GET  /api/analysis/excel/{{report_id}}              - Download Excel file")
    print()

if __name__ == "__main__":
    try:
        test_visualization_endpoints()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
