"""
Quick test to check if upload endpoint is accessible
"""
import requests
import os

BASE_URL = "http://localhost:8000"

# First login to get token
print("🔑 Logging in...")
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={
        "username": "test@example.com",
        "password": "TestPass123!"
    }
)

if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Login successful")
    print(f"Token: {token[:50]}...")
    
    # Check if PDF exists
    pdf_path = "microsoft_annual_report.pdf"
    if not os.path.exists(pdf_path):
        print(f"\n❌ PDF not found: {pdf_path}")
        print("Please provide a sample PDF to test with")
        exit(1)
    
    # Get PDF size
    pdf_size = os.path.getsize(pdf_path)
    print(f"\n📄 PDF file: {pdf_path}")
    print(f"📊 File size: {pdf_size:,} bytes ({pdf_size / 1024 / 1024:.2f} MB)")
    
    # Try upload with a very long timeout
    print(f"\n📤 Starting upload...")
    print("⏳ This will take several minutes. Please be patient...")
    print("💡 Tip: Watch the server terminal for progress updates")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(pdf_path, "rb") as pdf_file:
        files = {"file": (os.path.basename(pdf_path), pdf_file, "application/pdf")}
        data = {
            "company_name": "Microsoft Corporation",
            "report_year": 2024
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/upload/report",
                headers=headers,
                files=files,
                data=data,
                timeout=600  # 10 minute timeout
            )
            
            print(f"\n✅ Response received!")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                import json
                print(f"\n📊 Response:")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"\n❌ Error response:")
                print(response.text)
                
        except requests.exceptions.ReadTimeout:
            print(f"\n⚠️  Request timed out after 10 minutes!")
            print("Check server logs for errors")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
else:
    print(f"❌ Login failed: {response.status_code}")
    print(response.text)
