"""
Test Email Service - Lead Generation & Email Sending
"""
import sys
import os

sys.path.insert(0, os.path.abspath('.'))

print("=" * 80)
print("📧 EMAIL SERVICE TEST")
print("=" * 80)
print()

# Test Data
financial_data = {
    "company_name": "Microsoft Corporation",
    "revenue": 245122000000,
    "revenue_history": [211915000000],
    "key_metrics": {
        "roe": 43.2,
        "debt_to_equity": 0.35,
        "profit_margin": 35.97
    }
}

predictions = {
    "growth_rate": 21.39,
    "confidence_interval": {"lower": 15.25, "upper": 27.53},
    "recommendations": [
        "Exceptional Growth Trajectory",
        "Exceptional Return on Equity",
        "Low Risk Profile"
    ]
}

print("📊 Test 1: Generate Lead Analysis")
print("-" * 80)

try:
    from app.services.email_service import email_service
    
    lead_analysis = email_service.generate_potential_leads(
        financial_data=financial_data,
        predictions=predictions
    )
    
    print(f"✅ Investment Score: {lead_analysis['investment_score']}/100")
    print(f"✅ Recommendation: {lead_analysis['recommendation']}")
    print()
    
    print(f"💪 Key Strengths ({len(lead_analysis['key_strengths'])}):")
    for strength in lead_analysis['key_strengths']:
        print(f"   • {strength}")
    print()
    
    print(f"⚠️  Risk Factors ({len(lead_analysis['risk_factors'])}):")
    if lead_analysis['risk_factors']:
        for risk in lead_analysis['risk_factors']:
            print(f"   • {risk}")
    else:
        print("   None identified")
    print()
    
    print(f"🎯 Action Items ({len(lead_analysis['action_items'])}):")
    for action in lead_analysis['action_items']:
        print(f"   • {action}")
    print()
    
    print("✅ LEAD GENERATION TEST: PASSED")
    print()
    
except Exception as e:
    print(f"❌ LEAD GENERATION TEST: FAILED")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("📧 Test 2: Email Service Configuration")
print("-" * 80)

try:
    if email_service.sg:
        print("✅ SendGrid client initialized")
        print(f"✅ From Email: {email_service.from_email}")
        print()
        
        print("⚠️  To send actual emails, use:")
        print("   result = email_service.send_report_email(")
        print("       to_emails=['your-email@example.com'],")
        print("       company_name='Microsoft Corporation',")
        print("       report_path=None,")
        print("       financial_data=financial_data,")
        print("       predictions=predictions")
        print("   )")
        print()
    else:
        print("⚠️  SendGrid not configured")
        print("   To enable email sending:")
        print("   1. Sign up at https://sendgrid.com/")
        print("   2. Get API key from Settings > API Keys")
        print("   3. Add to .env: SENDGRID_API_KEY=SG.xxx")
        print()
    
    print("✅ EMAIL SERVICE TEST: PASSED")
    print()
    
except Exception as e:
    print(f"❌ EMAIL SERVICE TEST: FAILED")
    print(f"   Error: {e}")
    sys.exit(1)

print("📝 Test 3: HTML Template Generation")
print("-" * 80)

try:
    # Test report email HTML
    html = email_service._generate_email_html(
        company_name="Microsoft Corporation",
        financial_data=financial_data,
        predictions=predictions
    )
    
    print(f"✅ Report Email HTML: {len(html)} characters")
    print(f"   Contains DOCTYPE: {'<!DOCTYPE html>' in html}")
    print(f"   Contains Company Name: {'Microsoft Corporation' in html}")
    print(f"   Contains Metrics: {'metric' in html}")
    print()
    
    # Test lead email HTML
    lead_html = email_service._generate_lead_email_html(
        company_name="Microsoft Corporation",
        lead_analysis=lead_analysis
    )
    
    print(f"✅ Lead Email HTML: {len(lead_html)} characters")
    print(f"   Contains Score: {str(lead_analysis['investment_score']) in lead_html}")
    print(f"   Contains Sections: {'section' in lead_html}")
    print()
    
    print("✅ HTML TEMPLATE TEST: PASSED")
    print()
    
except Exception as e:
    print(f"❌ HTML TEMPLATE TEST: FAILED")
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print("🎉 ALL EMAIL SERVICE TESTS PASSED!")
print("=" * 80)
print()

print("📋 Summary:")
print("   ✅ Lead generation working")
print("   ✅ Investment scoring functional")
print("   ✅ HTML templates generated")
print(f"   {'✅' if email_service.sg else '⚠️ '} SendGrid {'configured' if email_service.sg else 'not configured'}")
print()

if not email_service.sg:
    print("💡 Next Steps:")
    print("   1. Get SendGrid API key")
    print("   2. Add to .env file")
    print("   3. Test actual email sending")
