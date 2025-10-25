"""
Test if CORS configuration is loaded correctly
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

print("=" * 60)
print("CORS CONFIGURATION TEST")
print("=" * 60)

print(f"\nCORS_ORIGINS (raw string):")
print(f"  {settings.CORS_ORIGINS}")

print(f"\ncors_origins_list (parsed list):")
for origin in settings.cors_origins_list:
    print(f"  - {origin}")

print(f"\nChecking for port 5174:")
if "http://localhost:5174" in settings.cors_origins_list:
    print("  ✅ Port 5174 is ALLOWED")
else:
    print("  ❌ Port 5174 is NOT ALLOWED")

print("\n" + "=" * 60)
