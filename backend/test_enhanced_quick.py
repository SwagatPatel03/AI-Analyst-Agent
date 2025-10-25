"""
Quick Test for Enhanced ML Predictor Service
"""
import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_predictor_enhanced import ml_predictor_enhanced


def convert_numpy(obj):
    """Convert numpy types"""
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def main():
    print("\n" + "="*80)
    print("TESTING ENHANCED ML PREDICTOR")
    print("="*80)
    
    # Load data
    json_path = "outputs/json/c0f206fd-5221-4b1a-88ca-78156f42fa80.json"
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract
    metadata = data.get('metadata', {})
    fs = data.get('financial_statements', {})
    ratios = data.get('financial_ratios', {})
    segments = data.get('segment_analysis', [])
    
    income = fs.get('income_statement', {})
    balance = fs.get('balance_sheet', {})
    curr_inc = income.get('current_year', {})
    prev_inc = income.get('previous_year', {})
    curr_bs = balance.get('current_year', {})
    
    financial_data = {
        'revenue': curr_inc.get('revenue', 0),
        'revenue_history': [prev_inc.get('revenue', 0), curr_inc.get('revenue', 0)],
        'net_income': curr_inc.get('net_income', 0),
        'net_income_history': [prev_inc.get('net_income', 0), curr_inc.get('net_income', 0)],
        'total_assets': curr_bs.get('total_assets', 0),
        'total_liabilities': curr_bs.get('total_liabilities', 0),
        'shareholders_equity': curr_bs.get('stockholders_equity', 0),
        'key_metrics': ratios,
        'segment_revenue': segments,
        'report_year': int(metadata.get('fiscal_year', 2024)),
        'company_name': metadata.get('company_name', 'Unknown')
    }
    
    print(f"\nCompany: {financial_data['company_name']}")
    print(f"Revenue: ${financial_data['revenue']:,.0f}M")
    
    # Predict
    print("\nGenerating predictions...")
    predictions = ml_predictor_enhanced.predict_growth_and_sales(
        financial_data=financial_data,
        report_id=1,
        scenarios=True,
        include_visualizations=True
    )
    
    if not predictions.get('success'):
        print(f"ERROR: {predictions.get('error')}")
        return
    
    print("SUCCESS!\n")
    
    # Display key results
    growth = predictions['growth_rate']
    print(f"Growth Rate: {growth['predicted']}% [{growth['confidence_lower']}%, {growth['confidence_upper']}%]")
    print(f"Historical: {growth['historical_growth']}%")
    print(f"Ensemble Confidence: {growth['ensemble_confidence']*100}%\n")
    
    print("5-Year Forecast:")
    for f in predictions['sales_forecast']:
        print(f"  {f['year']}: ${f['predicted_revenue']:,.0f}M")
    
    print("\nScenarios:")
    for name, s in predictions.get('scenarios', {}).items():
        print(f"  {name.replace('_', ' ').title()}: {s['growth_rate']}% (P={s['probability']*100}%)")
    
    risk = predictions['risk_metrics']
    print(f"\nRisk: {risk['risk_level']} (Score: {risk['risk_score']}/100)")
    print(f"Health: {risk['financial_health_score']}/100")
    print(f"VaR (95%): ${risk['value_at_risk_95']:,.0f}M")
    
    perf = predictions['performance_metrics']
    print(f"\nCAGR Historical: {perf['cagr_historical']}%")
    print(f"CAGR Projected (3Y): {perf['cagr_projected_3y']}%")
    print(f"ROIC: {perf['roic']}%")
    
    industry = predictions['industry_comparison']
    print(f"\nCompetitive Position: {industry['competitive_position']}")
    print(f"Outperforming: {industry['outperforming_count']}/{industry['total_metrics']} metrics")
    
    print(f"\nAnomaly Detection: {predictions['anomalies']['severity']}")
    print(f"Market Phase: {predictions['market_conditions']['market_phase']}")
    
    print(f"\nRecommendations: {len(predictions['recommendations'])}")
    for rec in predictions['recommendations'][:3]:
        print(f"  - {rec['title']}")
    
    # Save
    output = "outputs/json/ml_predictions_enhanced.json"
    with open(output, 'w') as f:
        json.dump(convert_numpy(predictions), f, indent=2)
    
    print(f"\nSaved to: {output}")
    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
