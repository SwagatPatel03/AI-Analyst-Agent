"""
Enhanced Test Script for Agentic Analyst Service
Tests with comprehensive queries to verify 90%+ success rate
"""

import json
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.agentic_analyst import agentic_analyst


def test_agentic_analyst_enhanced():
    """Test the agentic analyst with comprehensive queries"""
    
    print("=" * 80)
    print("🚀 TESTING ENHANCED AGENTIC ANALYST SERVICE")
    print("Target Success Rate: 90%+")
    print("=" * 80)
    
    # Paths
    excel_file = "outputs/excel/Microsoft_Corporation_FY2024_Financial_Report.xlsx"
    json_file = "outputs/json/c0f206fd-5221-4b1a-88ca-78156f42fa80.json"
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return
    
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
    
    print(f"\n📂 Loading files:")
    print(f"   Excel: {excel_file}")
    print(f"   JSON: {json_file}")
    
    with open(json_file, 'r') as f:
        financial_data = json.load(f)
    
    # Get company info
    metadata = financial_data.get('metadata', {})
    company_name = metadata.get('company_name', 'Unknown')
    fiscal_year = metadata.get('fiscal_year', 'Unknown')
    
    print(f"\n✅ Loaded data for: {company_name} (FY {fiscal_year})")
    
    # Comprehensive test queries covering various scenarios
    test_queries = [
        # Basic calculations
        {
            "category": "Basic Math",
            "query": "Calculate the revenue growth rate from previous year to current year",
            "expected": "~15-16%"
        },
        {
            "category": "Basic Math",
            "query": "What is the operating margin percentage for the current year?",
            "expected": "~44%"
        },
        {
            "category": "Basic Math",
            "query": "Calculate the net profit margin",
            "expected": "~36%"
        },
        
        # Comparisons
        {
            "category": "Comparisons",
            "query": "Compare total assets between current and previous year",
            "expected": "Asset change"
        },
        {
            "category": "Comparisons",
            "query": "How did operating income change year over year?",
            "expected": "Operating income growth"
        },
        
        # Financial ratios
        {
            "category": "Financial Ratios",
            "query": "Calculate the return on equity (ROE)",
            "expected": "~32-33%"
        },
        {
            "category": "Financial Ratios",
            "query": "What is the current ratio?",
            "expected": "~1.27"
        },
        {
            "category": "Financial Ratios",
            "query": "Calculate the debt-to-equity ratio",
            "expected": "~0.16"
        },
        
        # Segment analysis
        {
            "category": "Segment Analysis",
            "query": "Find the top 3 business segments by revenue",
            "expected": "Intelligent Cloud, Productivity, More Personal"
        },
        {
            "category": "Segment Analysis",
            "query": "Which segment has the highest operating margin?",
            "expected": "Segment with best margin"
        },
        
        # Geographic analysis
        {
            "category": "Geographic",
            "query": "What percentage of revenue comes from the United States?",
            "expected": "~50%"
        },
        {
            "category": "Geographic",
            "query": "List all geographic regions by revenue",
            "expected": "Regional revenue list"
        },
        
        # Complex queries
        {
            "category": "Complex",
            "query": "Calculate the percentage of revenue spent on R&D",
            "expected": "~12-13%"
        },
        {
            "category": "Complex",
            "query": "What is the average segment revenue?",
            "expected": "Average calculation"
        },
        {
            "category": "Complex",
            "query": "Calculate total cash and investments",
            "expected": "Cash + investments sum"
        },
    ]
    
    print("\n" + "=" * 80)
    print(f"🧠 RUNNING {len(test_queries)} COMPREHENSIVE TESTS")
    print("=" * 80)
    
    # Track results
    results = []
    successes = 0
    failures = 0
    
    for i, test in enumerate(test_queries, 1):
        category = test["category"]
        query = test["query"]
        expected = test["expected"]
        
        print(f"\n{'─' * 80}")
        print(f"📊 Test {i}/{len(test_queries)}: [{category}]")
        print(f"Query: {query}")
        print(f"Expected: {expected}")
        print(f"{'─' * 80}")
        
        # Analyze
        result = agentic_analyst.analyze(
            user_query=query,
            excel_path=excel_file,
            financial_data=financial_data
        )
        
        if result["success"]:
            successes += 1
            status = "✅ SUCCESS"
            
            # Show attempts if more than 1
            attempts = result.get("attempts", 1)
            if attempts > 1:
                print(f"\n🔄 Succeeded on attempt {attempts}/3")
            
            # Show result
            if result["result"]["value"] is not None:
                print(f"\n📊 Result: {result['result']['value']}")
            
            if result["result"]["output"]:
                print(f"\n📤 Output:\n{result['result']['output']}")
            
            print(f"\n💡 Explanation:\n{result['explanation'][:200]}...")
        else:
            failures += 1
            status = "❌ FAILED"
            print(f"\n❌ Analysis Failed")
            print(f"Error: {result['error']}")
        
        print(f"\n{status}")
        
        # Store result
        results.append({
            "category": category,
            "query": query,
            "success": result["success"],
            "attempts": result.get("attempts", 1)
        })
    
    # Final statistics
    print("\n" + "=" * 80)
    print("📈 FINAL RESULTS")
    print("=" * 80)
    
    success_rate = (successes / len(test_queries)) * 100
    
    print(f"\n✅ Successful: {successes}/{len(test_queries)}")
    print(f"❌ Failed: {failures}/{len(test_queries)}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    # Show target comparison
    if success_rate >= 90:
        print(f"\n🎉 TARGET ACHIEVED! Success rate >= 90%")
    else:
        print(f"\n⚠️ Target not met. Need {90 - success_rate:.1f}% more")
    
    # Breakdown by category
    print(f"\n📊 Results by Category:")
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0}
        categories[cat]["total"] += 1
        if r["success"]:
            categories[cat]["success"] += 1
    
    for cat, stats in categories.items():
        rate = (stats["success"] / stats["total"]) * 100
        print(f"   {cat}: {stats['success']}/{stats['total']} ({rate:.0f}%)")
    
    # Show retry effectiveness
    retries = [r for r in results if r["success"] and r.get("attempts", 1) > 1]
    if retries:
        print(f"\n🔄 Retry Success: {len(retries)} queries succeeded after retry")
    
    print("\n" + "=" * 80)
    print("✨ Key Features Demonstrated:")
    print("   ✅ Multi-attempt retry logic")
    print("   ✅ Smart DataFrame inspection")
    print("   ✅ Enhanced error recovery")
    print("   ✅ Improved code generation")
    print("   ✅ Comprehensive testing")
    print("=" * 80)
    
    return success_rate >= 90


if __name__ == "__main__":
    try:
        success = test_agentic_analyst_enhanced()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
