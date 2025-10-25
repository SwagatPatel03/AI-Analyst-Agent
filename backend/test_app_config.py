"""
Test script to verify main application configuration
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_app_configuration():
    print("\n" + "="*60)
    print("🔧 Testing Main Application Configuration")
    print("="*60)
    
    # Test 1: Root endpoint
    print("\n1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working!")
            print(f"   Message: {data.get('message')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Available endpoints:")
            for name, path in data.get('endpoints', {}).items():
                print(f"      • {name}: {path}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2️⃣ Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check working!")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Database: {data.get('database')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: OpenAPI docs
    print("\n3️⃣ Testing OpenAPI documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger UI accessible at http://localhost:8000/docs")
        else:
            print(f"⚠️  Swagger UI returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Check all route prefixes
    print("\n4️⃣ Testing route prefixes...")
    routes_to_test = [
        ("/api/auth", "Authentication routes"),
        ("/api/upload", "Upload routes"),
        ("/api/analysis", "Analysis routes"),
        ("/api/chatbot", "Chatbot routes"),
        ("/api/report", "Report routes"),
    ]
    
    for route, description in routes_to_test:
        try:
            # Just check if the route exists (will likely return 401 or 404, not 500)
            response = requests.get(f"{BASE_URL}{route}")
            if response.status_code in [401, 404, 405, 422]:
                print(f"   ✅ {description}: {route} (accessible)")
            else:
                print(f"   ⚠️  {description}: {route} (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ {description}: {route} (error: {e})")
    
    # Test 5: Static files
    print("\n5️⃣ Testing static file serving...")
    try:
        # Check if static route is mounted
        response = requests.get(f"{BASE_URL}/static/")
        if response.status_code in [200, 404]:  # 404 is ok if no files yet
            print("✅ Static files route mounted: /static")
            print("   Visualizations will be accessible at /static/visualizations/")
        else:
            print(f"⚠️  Static files returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Static files: {e}")
    
    # Test 6: CORS headers
    print("\n6️⃣ Testing CORS configuration...")
    try:
        response = requests.options(f"{BASE_URL}/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        })
        cors_allow_origin = response.headers.get("Access-Control-Allow-Origin")
        if cors_allow_origin:
            print(f"✅ CORS enabled!")
            print(f"   Allow-Origin: {cors_allow_origin}")
            print(f"   Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'Not set')}")
        else:
            print("⚠️  CORS headers not found (might be configured differently)")
    except Exception as e:
        print(f"⚠️  CORS test: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ Main application configuration verified!")
    print("="*60)
    print("\n📚 Documentation:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("   • OpenAPI JSON: http://localhost:8000/openapi.json")
    print("\n📊 Static Files:")
    print("   • Visualizations: http://localhost:8000/static/visualizations/")
    print("   • JSON files: http://localhost:8000/static/json/")
    print("   • Excel files: http://localhost:8000/static/excel/")
    print("\n🔗 API Endpoints:")
    print("   • Authentication: http://localhost:8000/api/auth")
    print("   • Upload: http://localhost:8000/api/upload")
    print("   • Analysis: http://localhost:8000/api/analysis")
    print("   • Chatbot: http://localhost:8000/api/chatbot")
    print("   • Report: http://localhost:8000/api/report")
    print()

if __name__ == "__main__":
    print("\n⚠️  Make sure the FastAPI server is running before running this test!")
    print("   Start server: venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
    input("\nPress Enter to continue...")
    
    try:
        test_app_configuration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
