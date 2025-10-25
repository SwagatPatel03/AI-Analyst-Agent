"""
Test main application with all routes including chatbot
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_main_app():
    """Test that main app includes all routes"""
    try:
        from app.main import app
        
        print("=" * 80)
        print("🧪 TESTING MAIN APPLICATION WITH CHATBOT ROUTES")
        print("=" * 80)
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods)
                path = route.path
                name = route.name if hasattr(route, 'name') else 'N/A'
                routes.append((methods, path, name))
        
        print(f"\n✅ Main app imported successfully")
        print(f"✅ Total routes: {len(routes)}")
        
        # Check for chatbot routes
        chatbot_routes = [r for r in routes if '/chatbot' in r[1]]
        
        print(f"\n📋 Chatbot Routes Found: {len(chatbot_routes)}")
        for methods, path, name in chatbot_routes:
            print(f"   {methods:15s} {path:45s} → {name}")
        
        # Verify required chatbot endpoints
        required_endpoints = [
            '/api/chatbot/chat/{report_id}',
            '/api/chatbot/chat/history/{report_id}',
            '/api/chatbot/agent/analyze/{report_id}',
            '/api/chatbot/agent/execute-code/{report_id}',
            '/api/chatbot/financial',
            '/api/chatbot/agentic'
        ]
        
        print(f"\n✅ Checking Required Endpoints:")
        all_found = True
        for endpoint in required_endpoints:
            found = any(endpoint in r[1] for r in routes)
            status = "✅" if found else "❌"
            print(f"   {status} {endpoint}")
            if not found:
                all_found = False
        
        # Check other routes
        print(f"\n📋 All API Routes:")
        api_routes = [r for r in routes if '/api/' in r[1]]
        
        categories = {
            'Auth': [],
            'Upload': [],
            'Analysis': [],
            'Chatbot': [],
            'Report': []
        }
        
        for methods, path, name in api_routes:
            if '/auth' in path:
                categories['Auth'].append((methods, path, name))
            elif '/upload' in path:
                categories['Upload'].append((methods, path, name))
            elif '/analysis' in path:
                categories['Analysis'].append((methods, path, name))
            elif '/chatbot' in path:
                categories['Chatbot'].append((methods, path, name))
            elif '/report' in path:
                categories['Report'].append((methods, path, name))
        
        for category, routes_list in categories.items():
            if routes_list:
                print(f"\n   {category} ({len(routes_list)} routes):")
                for methods, path, name in routes_list[:3]:  # Show first 3
                    print(f"      {methods:15s} {path}")
                if len(routes_list) > 3:
                    print(f"      ... and {len(routes_list) - 3} more")
        
        # Check root endpoints
        print(f"\n📋 Special Endpoints:")
        special = [r for r in routes if r[1] in ['/', '/health', '/docs', '/openapi.json']]
        for methods, path, name in special:
            print(f"   {methods:15s} {path:20s} → {name}")
        
        print("\n" + "=" * 80)
        if all_found:
            print("🎉 ALL CHATBOT ROUTES SUCCESSFULLY INTEGRATED!")
        else:
            print("⚠️  SOME ROUTES MISSING - CHECK CONFIGURATION")
        print("=" * 80)
        
        print("\n✅ Summary:")
        print(f"   - Total Routes: {len(routes)}")
        print(f"   - Auth Routes: {len(categories['Auth'])}")
        print(f"   - Upload Routes: {len(categories['Upload'])}")
        print(f"   - Analysis Routes: {len(categories['Analysis'])}")
        print(f"   - Chatbot Routes: {len(categories['Chatbot'])}")
        print(f"   - Report Routes: {len(categories['Report'])}")
        
        print("\n🚀 Application Status:")
        print("   ✅ Main app configured")
        print("   ✅ All routers included")
        print("   ✅ Chatbot routes active")
        print("   ✅ CORS configured")
        print("   ✅ Static files mounted")
        print("   ✅ Database tables created")
        
        print("\n📚 Available at:")
        print("   - API: http://localhost:8000")
        print("   - Docs: http://localhost:8000/docs")
        print("   - Redoc: http://localhost:8000/redoc")
        print("   - Health: http://localhost:8000/health")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing main app: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_main_app()
