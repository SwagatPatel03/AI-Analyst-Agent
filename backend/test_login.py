"""
Test login endpoint directly
"""
import requests
import json

print("=" * 60)
print("TESTING LOGIN ENDPOINT")
print("=" * 60)

# Test data
email = "swagatpatel03@gmail.com"
password = "swagat03"

print(f"\n📧 Email: {email}")
print(f"🔑 Password: {password}")
print(f"\n🔗 Testing: POST http://localhost:8000/auth/login")

try:
    response = requests.post(
        "http://localhost:8000/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📄 Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ LOGIN SUCCESSFUL!")
        print(f"🎟️  Access Token: {response.json().get('access_token', 'N/A')[:50]}...")
    else:
        print("\n❌ LOGIN FAILED!")
        print(f"Error: {response.json().get('detail', 'Unknown error')}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend!")
    print("Make sure backend is running: python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
