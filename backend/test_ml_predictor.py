"""
Test ML Predictor Service
"""
import sys
import os
import json
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_predictor import ml_predictor


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def test_ml_predictor():
    """Test ML predictor with Microsoft financial data"""
    
    print("=" * 80)
    print("🧪 TESTING ML PREDICTOR SERVICE")
    print("=" * 80)
    
    # Load test data
    json_files = [f for f in os.listdir("outputs/json") if f.endswith('.json')]
    
    if not json_files:
        print("❌ No JSON files found in outputs/json/")
        return False
    
    json_path = os.path.join("outputs/json", json_files[0])
    
    print(f"\n📂 Loading data from: {json_path}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract financial data from the structure
    metadata = data.get('metadata', {})
    financial_statements = data.get('financial_statements', {})
    financial_ratios = data.get('financial_ratios', {})
    segment_analysis = data.get('segment_analysis', [])
    
    # Build financial_data structure for ML predictor
    income_statement = financial_statements.get('income_statement', {})
    balance_sheet = financial_statements.get('balance_sheet', {})
    
    # Extract from year-based structure
    current_year_income = income_statement.get('current_year', {})
    previous_year_income = income_statement.get('previous_year', {})
    current_year_bs = balance_sheet.get('current_year', {})
    previous_year_bs = balance_sheet.get('previous_year', {})
    
    financial_data = {
        'revenue': current_year_income.get('revenue', 0),
        'revenue_history': [previous_year_income.get('revenue', 0), current_year_income.get('revenue', 0)],
        'net_income': current_year_income.get('net_income', 0),
        'net_income_history': [previous_year_income.get('net_income', 0), current_year_income.get('net_income', 0)],
        'total_assets': current_year_bs.get('total_assets', 0),
        'total_liabilities': current_year_bs.get('total_liabilities', 0),
        'shareholders_equity': current_year_bs.get('stockholders_equity', 0) or current_year_bs.get('total_equity', 0),
        'key_metrics': financial_ratios,
        'segment_revenue': segment_analysis if isinstance(segment_analysis, list) else [],
        'report_year': int(metadata.get('fiscal_year', 2024)),
        'company_name': metadata.get('company_name', 'Unknown')
    }
    
    print(f"✅ Loaded financial data for: {financial_data.get('company_name', 'Unknown')}")
    
    # Test predictions
    print("\n" + "=" * 80)
    print("🔮 GENERATING PREDICTIONS")
    print("=" * 80)
    
    try:
        print(f"📊 Revenue: {financial_data.get('revenue')}")
        print(f"📊 Revenue History: {financial_data.get('revenue_history')}")
        print(f"📊 Net Income: {financial_data.get('net_income')}")
        print(f"📊 Total Assets: {financial_data.get('total_assets')}")
        
        predictions = ml_predictor.predict_growth_and_sales(
            financial_data=financial_data,
            report_id=1
        )
        
        if not predictions.get('success'):
            print(f"❌ Prediction failed: {predictions.get('error')}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ Predictions generated successfully!")
        
        # Display results
        print("\n📊 GROWTH PREDICTION:")
        growth = predictions['growth_rate']
        print(f"   Predicted Growth Rate: {growth['predicted']}%")
        print(f"   Confidence Interval: [{growth['confidence_lower']}%, {growth['confidence_upper']}%]")
        print(f"   Historical Growth: {growth.get('historical_growth', 'N/A')}%")
        print(f"   Confidence Level: {growth['confidence_level'] * 100}%")
        
        print("\n📈 SALES FORECAST (Next 3 Years):")
        for forecast in predictions['sales_forecast']:
            year = forecast['year']
            revenue = forecast['predicted_revenue']
            lower = forecast['confidence_lower']
            upper = forecast['confidence_upper']
            currency = forecast['currency']
            
            print(f"   Year {year}: {currency} {revenue:,.0f}")
            print(f"      Confidence Range: [{currency} {lower:,.0f}, {currency} {upper:,.0f}]")
        
        print("\n🎯 SEGMENT BREAKDOWN:")
        segments = predictions.get('segment_breakdown', [])
        if segments:
            for segment in segments:
                name = segment['segment']
                current = segment['current_revenue']
                predicted = segment['predicted_revenue']
                growth = segment['predicted_growth']
                proportion = segment['proportion']
                
                print(f"   {name}:")
                print(f"      Current: ${current:,.0f}M ({proportion:.1f}%)")
                print(f"      Predicted: ${predicted:,.0f}M (Growth: {growth:+.2f}%)")
        else:
            print("   No segment data available")
        
        print("\n⚠️ RISK METRICS:")
        risk = predictions['risk_metrics']
        print(f"   Overall Risk Level: {risk['risk_level']}")
        print(f"   Risk Score: {risk['risk_score']}/100")
        print(f"   Financial Health Score: {risk['financial_health_score']}/100")
        print(f"   Volatility: {risk['volatility']}%")
        print(f"   Debt Risk: {risk['debt_risk']}")
        print(f"   Growth Uncertainty: {risk['growth_uncertainty']}")
        
        print("\n💡 INVESTMENT RECOMMENDATIONS:")
        for i, rec in enumerate(predictions['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print("\n📚 METHODOLOGY:")
        print(f"   {predictions['methodology']}")
        print(f"   Model Accuracy: {predictions['model_accuracy']}")
        
        print("\n" + "=" * 80)
        print("🎉 ML PREDICTOR TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        # Save predictions (convert numpy types first)
        output_file = "outputs/json/ml_predictions_test.json"
        predictions_json = convert_numpy_types(predictions)
        with open(output_file, 'w') as f:
            json.dump(predictions_json, f, indent=2)
        
        print(f"\n💾 Predictions saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n" + "=" * 80)
    print("🧪 TESTING EDGE CASES")
    print("=" * 80)
    
    # Test 1: Empty data
    print("\n1️⃣ Testing with empty data...")
    result = ml_predictor.predict_growth_and_sales({}, 1)
    if not result['success']:
        print(f"   ✅ Correctly handled empty data: {result['error']}")
    else:
        print("   ❌ Should have failed with empty data")
    
    # Test 2: Minimal data
    print("\n2️⃣ Testing with minimal data...")
    minimal_data = {
        'revenue': {'current_year': 100000, 'previous_year': 90000},
        'report_year': 2024
    }
    result = ml_predictor.predict_growth_and_sales(minimal_data, 2)
    if result['success']:
        print(f"   ✅ Handled minimal data successfully")
        print(f"   Growth Rate: {result['growth_rate']['predicted']}%")
    else:
        print(f"   ❌ Failed with minimal data: {result['error']}")
    
    # Test 3: No historical data
    print("\n3️⃣ Testing with no historical data...")
    no_history = {
        'revenue': {'current_year': 100000, 'previous_year': 0},
        'report_year': 2024
    }
    result = ml_predictor.predict_growth_and_sales(no_history, 3)
    if result['success']:
        print(f"   ✅ Used industry average: {result['growth_rate']['predicted']}%")
    else:
        print(f"   ❌ Failed: {result['error']}")
    
    print("\n✅ Edge case testing completed!")


if __name__ == "__main__":
    success = test_ml_predictor()
    
    if success:
        test_edge_cases()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED")
    print("=" * 80)
