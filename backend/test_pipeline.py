"""
Test script for the complete upload and processing pipeline
Run this after starting the FastAPI server
"""
import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PDF = "microsoft_annual_report.pdf"  # You'll need to provide this
COMPANY_NAME = "Microsoft Corporation"
REPORT_YEAR = 2024

class PipelineTester:
    def __init__(self):
        self.token = None
        self.report_id = None
        self.test_user = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
    
    def test_1_register_user(self):
        """Test 1: Register a test user"""
        print("\n" + "="*60)
        print("TEST 1: User Registration")
        print("="*60)
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=self.test_user
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("✅ User registration successful!")
            return True
        elif response.status_code == 400:
            # Check if user already exists
            try:
                error_detail = response.json().get("detail", "")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                if "already" in error_detail.lower() or "exists" in error_detail.lower() or "registered" in error_detail.lower():
                    print("⚠️  User already exists, will try to login")
                    return True
                else:
                    print("❌ User registration failed!")
                    return False
            except:
                print(f"Response: {response.text}")
                print("❌ User registration failed!")
                return False
        else:
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response: {response.text}")
            print("❌ User registration failed!")
            return False
    
    def test_2_login_user(self):
        """Test 2: Login and get JWT token"""
        print("\n" + "="*60)
        print("TEST 2: User Login")
        print("="*60)
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={
                "username": self.test_user["email"],
                "password": self.test_user["password"]
            }
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            print(f"✅ Login successful!")
            print(f"Token: {self.token[:50]}...")
            return True
        else:
            print(f"❌ Login failed!")
            print(f"Response: {response.text}")
            return False
    
    def test_3_upload_report(self, pdf_path):
        """Test 3: Upload PDF and process"""
        print("\n" + "="*60)
        print("TEST 3: Upload and Process PDF")
        print("="*60)
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            print(f"Please place a sample annual report PDF at: {pdf_path}")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with open(pdf_path, "rb") as pdf_file:
            files = {"file": (os.path.basename(pdf_path), pdf_file, "application/pdf")}
            data = {
                "company_name": COMPANY_NAME,
                "report_year": REPORT_YEAR
            }
            
            print(f"Uploading: {pdf_path}")
            print(f"Company: {COMPANY_NAME}")
            print(f"Year: {REPORT_YEAR}")
            print("Processing... (this may take 2-5 minutes for Groq API calls)")
            print("⏳ Please wait, the server is calling AI to extract financial data...")
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/upload/report",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=600  # 5 minute timeout for AI processing
                )
            except requests.exceptions.ReadTimeout:
                print(f"\n⚠️  Request timed out after 5 minutes")
                print(f"This usually means:")
                print(f"  1. The PDF is very large and taking a long time to process")
                print(f"  2. The Groq API is slow or rate-limited")
                print(f"  3. There's an error on the server side")
                print(f"\n💡 Check the server logs for more details")
                return False
            except requests.exceptions.ConnectionError as e:
                print(f"\n❌ Connection error: {e}")
                print(f"Make sure the FastAPI server is running at {BASE_URL}")
                return False
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.report_id = data.get("report_id")
            print(f"✅ Upload and processing successful!")
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Upload failed!")
            print(f"Response: {response.text}")
            return False
    
    def test_4_verify_json(self):
        """Test 4: Verify JSON file was created"""
        print("\n" + "="*60)
        print("TEST 4: Verify JSON Extraction")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{BASE_URL}/api/upload/report/{self.report_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            json_path = data.get("json_path")
            
            if json_path and os.path.exists(json_path):
                print(f"✅ JSON file exists: {json_path}")
                
                # Read and display JSON content
                with open(json_path, 'r') as f:
                    json_data = json.load(f)
                
                print(f"\nJSON Content Preview:")
                print(json.dumps(json_data, indent=2)[:1000] + "...")
                return True
            else:
                print(f"❌ JSON file not found: {json_path}")
                return False
        else:
            print(f"❌ Failed to get report details")
            return False
    
    def test_5_verify_excel(self):
        """Test 5: Verify Excel file was created"""
        print("\n" + "="*60)
        print("TEST 5: Verify Excel Generation")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{BASE_URL}/api/upload/report/{self.report_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            excel_path = data.get("excel_path")
            
            if excel_path and os.path.exists(excel_path):
                file_size = os.path.getsize(excel_path)
                print(f"✅ Excel file exists: {excel_path}")
                print(f"File size: {file_size:,} bytes")
                
                # Try to read Excel and show sheet names
                try:
                    import pandas as pd
                    excel_file = pd.ExcelFile(excel_path)
                    print(f"\nExcel Sheets:")
                    for sheet in excel_file.sheet_names:
                        print(f"  - {sheet}")
                    print(f"\n✅ Excel file is valid and readable!")
                    return True
                except Exception as e:
                    print(f"⚠️  Excel file exists but could not read: {e}")
                    return True
            else:
                print(f"❌ Excel file not found: {excel_path}")
                return False
        else:
            print(f"❌ Failed to get report details")
            return False
    
    def test_6_verify_database(self):
        """Test 6: Verify database was updated"""
        print("\n" + "="*60)
        print("TEST 6: Verify Database Updates")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get all reports
        response = requests.get(
            f"{BASE_URL}/api/upload/reports",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            reports = data.get("reports", [])
            
            print(f"✅ Found {len(reports)} report(s) in database")
            
            # Find our test report
            test_report = None
            for report in reports:
                if report["id"] == self.report_id:
                    test_report = report
                    break
            
            if test_report:
                print(f"\nTest Report Details:")
                print(json.dumps(test_report, indent=2, default=str))
                
                if test_report.get("status") == "completed":
                    print(f"\n✅ Report status is 'completed'")
                    return True
                else:
                    print(f"\n⚠️  Report status is '{test_report.get('status')}' (expected 'completed')")
                    return False
            else:
                print(f"❌ Test report not found in database")
                return False
        else:
            print(f"❌ Failed to retrieve reports from database")
            return False
    
    def test_7_cleanup(self):
        """Test 7: Optional - Delete test report"""
        print("\n" + "="*60)
        print("TEST 7: Cleanup (Optional)")
        print("="*60)
        
        cleanup = input("\nDo you want to delete the test report? (y/n): ").lower()
        
        if cleanup == 'y':
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(
                f"{BASE_URL}/api/upload/report/{self.report_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ Test report deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete test report")
                return False
        else:
            print("⏭️  Skipping cleanup")
            return True
    
    def run_all_tests(self, pdf_path):
        """Run all tests in sequence"""
        print("\n" + "🔬"*30)
        print("UPLOAD & PROCESSING PIPELINE TEST SUITE")
        print("🔬"*30)
        
        results = []
        
        # Test 1: Register
        results.append(("User Registration", self.test_1_register_user()))
        
        # Test 2: Login
        if results[-1][1]:
            results.append(("User Login", self.test_2_login_user()))
        else:
            print("\n❌ Skipping remaining tests due to registration failure")
            return
        
        # Test 3: Upload
        if results[-1][1]:
            results.append(("Upload & Process PDF", self.test_3_upload_report(pdf_path)))
        else:
            print("\n❌ Skipping remaining tests due to login failure")
            return
        
        # Test 4: Verify JSON
        if results[-1][1]:
            results.append(("JSON Verification", self.test_4_verify_json()))
        
        # Test 5: Verify Excel
        if results[-1][1]:
            results.append(("Excel Verification", self.test_5_verify_excel()))
        
        # Test 6: Verify Database
        if results[-1][1]:
            results.append(("Database Verification", self.test_6_verify_database()))
        
        # Test 7: Cleanup
        results.append(("Cleanup", self.test_7_cleanup()))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, passed in results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name:<30} {status}")
        
        passed_count = sum(1 for _, passed in results if passed)
        total_count = len(results)
        
        print(f"\nTotal: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("\n🎉 All tests passed! Pipeline is working correctly!")
        else:
            print(f"\n⚠️  {total_count - passed_count} test(s) failed. Please check the errors above.")


if __name__ == "__main__":
    print("="*60)
    print("PIPELINE TESTING PREREQUISITES")
    print("="*60)
    print("\n1. Make sure PostgreSQL is running")
    print("2. Make sure database 'ai_analyst_db' is created")
    print("3. Make sure Alembic migrations have been run")
    print("4. Make sure FastAPI server is running (uvicorn app.main:app --reload)")
    print("5. Make sure you have a sample annual report PDF")
    print("6. Make sure you have Groq API key configured in .env")
    print("\nNote: SendGrid/Email is NOT required for this test!")
    print("\n" + "="*60)
    
    proceed = input("\nAre all prerequisites met? (y/n): ").lower()
    
    if proceed != 'y':
        print("\n⏸️  Please complete the prerequisites and run this script again.")
        exit()
    
    # Get PDF path
    pdf_path = input(f"\nEnter the path to your test PDF (or press Enter to use '{TEST_PDF}'): ").strip()
    if not pdf_path:
        pdf_path = TEST_PDF
    
    # Run tests
    tester = PipelineTester()
    tester.run_all_tests(pdf_path)
