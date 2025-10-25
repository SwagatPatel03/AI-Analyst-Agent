"""
Test script for visualization service
"""
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from app.services.visualization_service import VisualizationService

# Sample financial data
sample_data = {
    "financial_metrics": {
        "total_revenue": 198270,
        "previous_revenue": 184903,
        "net_income": 72361,
        "total_assets": 411976,
        "total_liabilities": 255020,
        "shareholders_equity": 118304,
        "operating_cash_flow": 87582,
        "investing_cash_flow": -23200,
        "financing_cash_flow": -10500
    },
    "kpis": {
        "eps": 2.99,
        "pe_ratio": 18.5,
        "roe": 26.4,
        "debt_to_equity": 1.57,
        "net_profit_margin": 25.88,
        "roa": 17.58
    },
    "segments": [
        {"name": "iPhone", "revenue": 100453},
        {"name": "Mac", "revenue": 31185},
        {"name": "iPad", "revenue": 21745},
        {"name": "Wearables", "revenue": 31185},
        {"name": "Services", "revenue": 31745}
    ],
    "geographic": [
        {"region": "Americas", "revenue": 82959},
        {"region": "Europe", "revenue": 68640},
        {"region": "Greater China", "revenue": 15758},
        {"region": "Japan", "revenue": 6755},
        {"region": "Rest of Asia Pacific", "revenue": 24158}
    ]
}

def test_visualizations():
    print("🎨 Testing Visualization Service...\n")
    
    # Initialize service
    service = VisualizationService()
    
    # Test analysis ID
    test_analysis_id = 999
    
    try:
        # Generate all visualizations
        print("📊 Generating visualizations...")
        results = service.generate_all_visualizations(sample_data, test_analysis_id)
        
        print(f"\n✅ Successfully generated {len(results)} visualizations:")
        for chart_name, file_path in results.items():
            print(f"  • {chart_name}: {file_path}")
        
        # Verify files exist
        print("\n🔍 Verifying files...")
        all_exist = True
        for chart_name, file_path in results.items():
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✓ {chart_name}: {size:,} bytes")
            else:
                print(f"  ✗ {chart_name}: FILE NOT FOUND")
                all_exist = False
        
        if all_exist:
            print("\n🎉 All visualizations created successfully!")
            print(f"📂 Output directory: {service.output_dir}")
            return True
        else:
            print("\n⚠️ Some visualizations were not created")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visualizations()
    sys.exit(0 if success else 1)
