from groq import Groq
from app.config import settings
from typing import List, Dict, Any
import json
import re

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # 128k context - Best for chat/conversation
        self.code_model = "qwen/qwen3-32b"  # Best for code generation/agentic tasks
    
    def create_comprehensive_extraction_prompt(self, company_name: str) -> str:
        """Create a comprehensive prompt for extracting ALL financial data"""
        return f"""You are an expert financial analyst with deep knowledge of financial statements, annual reports, and SEC filings. 

Your task is to perform a COMPLETE and THOROUGH extraction of ALL financial information from the {company_name} annual report provided below.

EXTRACTION REQUIREMENTS:

1. COMPANY METADATA:
   - company_name, fiscal_year, reporting_period (start/end dates), currency, fiscal_quarter
   - auditor_name, auditor_opinion, report_date, cik_number (if available)

2. INCOME STATEMENT (Profit & Loss):
   - Extract for BOTH current year AND previous year where available
   - revenue (total), cost_of_revenue, gross_profit
   - research_and_development, sales_and_marketing, general_and_administrative
   - total_operating_expenses, operating_income, operating_margin
   - interest_income, interest_expense, other_income_expense
   - income_before_tax, income_tax_expense, effective_tax_rate
   - net_income, net_income_margin
   - basic_eps, diluted_eps, weighted_average_shares
   - ebitda, ebit

3. BALANCE SHEET:
   - Extract for BOTH current year AND previous year where available
   - ASSETS: cash_and_cash_equivalents, short_term_investments, accounts_receivable, 
     inventory, prepaid_expenses, other_current_assets, total_current_assets
   - property_plant_equipment, accumulated_depreciation, intangible_assets, goodwill,
     long_term_investments, other_non_current_assets, total_non_current_assets, total_assets
   - LIABILITIES: accounts_payable, accrued_expenses, short_term_debt, current_portion_long_term_debt,
     other_current_liabilities, total_current_liabilities
   - long_term_debt, deferred_tax_liabilities, other_long_term_liabilities,
     total_non_current_liabilities, total_liabilities
   - EQUITY: common_stock, preferred_stock, additional_paid_in_capital, retained_earnings,
     treasury_stock, accumulated_other_comprehensive_income, total_shareholders_equity

4. CASH FLOW STATEMENT:
   - OPERATING: net_income, depreciation_amortization, stock_based_compensation,
     deferred_income_taxes, changes_in_working_capital, other_operating_activities,
     net_cash_from_operating_activities
   - INVESTING: capital_expenditures, acquisitions, purchases_of_investments,
     sales_of_investments, other_investing_activities, net_cash_from_investing_activities
   - FINANCING: proceeds_from_debt, repayment_of_debt, dividends_paid, stock_repurchases,
     proceeds_from_stock_issuance, other_financing_activities, net_cash_from_financing_activities
   - net_change_in_cash, cash_beginning_of_period, cash_end_of_period, free_cash_flow

5. KEY PERFORMANCE INDICATORS & RATIOS:
   - PROFITABILITY: gross_margin, operating_margin, net_profit_margin, roe, roa, roic
   - LIQUIDITY: current_ratio, quick_ratio, cash_ratio, working_capital
   - LEVERAGE: debt_to_equity, debt_to_assets, interest_coverage, debt_service_coverage
   - EFFICIENCY: asset_turnover, inventory_turnover, receivables_turnover, days_sales_outstanding
   - VALUATION: price_to_earnings, price_to_book, price_to_sales, ev_to_ebitda, market_cap
   - GROWTH: revenue_growth_yoy, net_income_growth_yoy, eps_growth_yoy, asset_growth_yoy
   - PER SHARE: book_value_per_share, revenue_per_share, cash_per_share, fcf_per_share

6. BUSINESS SEGMENTS:
   - For each segment extract: segment_name, segment_revenue, segment_operating_income,
     segment_assets, segment_depreciation, segment_capital_expenditure
   - Include BOTH current and prior year data
   - Calculate segment_margin for each

7. GEOGRAPHIC BREAKDOWN:
   - For each region: region_name, region_revenue, region_operating_income, region_assets
   - Include major countries or regions mentioned
   - Calculate as percentage of total

8. MANAGEMENT DISCUSSION & ANALYSIS (MD&A):
   - business_overview (comprehensive summary)
   - key_strategies (list of strategic initiatives)
   - competitive_position (market position description)
   - market_opportunities (identified opportunities)
   - key_risks (list all risk factors mentioned)
   - management_outlook (forward-looking statements)
   - significant_events (acquisitions, divestitures, restructuring)
   - regulatory_matters (legal, compliance issues)

9. OPERATIONAL METRICS:
   - employee_count, employee_growth_rate
   - customer_count, customer_acquisition_cost, customer_lifetime_value
   - active_users, monthly_active_users, daily_active_users (if tech company)
   - subscriber_count, subscriber_growth, churn_rate (if subscription business)
   - average_revenue_per_user, gross_merchandise_value (if applicable)
   - store_count, same_store_sales_growth (if retail)
   - production_volume, capacity_utilization (if manufacturing)

10. DIVIDENDS & SHAREHOLDER RETURNS:
    - dividend_per_share, dividend_yield, dividend_payout_ratio
    - total_dividends_paid, share_repurchases, total_shareholder_returns

11. ESG & SUSTAINABILITY:
    - carbon_emissions, renewable_energy_percentage
    - diversity_metrics, board_diversity
    - esg_initiatives, sustainability_goals
    - social_responsibility_programs

12. CEO LETTER / LEADERSHIP COMMENTARY:
    - Extract key themes, accomplishments, challenges, future vision
    - Summarize in ceo_statement_summary

CRITICAL INSTRUCTIONS:
- Extract ACTUAL NUMBERS from the financial statements
- For monetary values, report in MILLIONS (e.g., $245.122 billion = 245122)
- Include BOTH current year (most recent) AND previous year data
- If a value is not found or not disclosed, use null
- Calculate year-over-year growth rates where possible
- Use proper data types: numbers for financial values, strings for text, arrays for lists
- Return a comprehensive JSON structure with nested objects for organization
- Do NOT make up data - only extract what is explicitly stated or clearly calculable

RESPONSE FORMAT:
Return ONLY a valid JSON object. No markdown, no explanations, just pure JSON.

Structure your response like this (expand with all extracted data):
{{
  "metadata": {{...}},
  "financial_statements": {{
    "income_statement": {{
      "current_year": {{...}},
      "previous_year": {{...}}
    }},
    "balance_sheet": {{
      "current_year": {{...}},
      "previous_year": {{...}}
    }},
    "cash_flow": {{
      "current_year": {{...}},
      "previous_year": {{...}}
    }}
  }},
  "financial_ratios": {{...}},
  "segment_analysis": [...],
  "geographic_analysis": [...],
  "management_analysis": {{...}},
  "operational_metrics": {{...}},
  "shareholder_returns": {{...}},
  "esg_data": {{...}}
}}

BEGIN EXTRACTION NOW."""
    
    def extract_financial_data(self, text_content: str, company_name: str) -> Dict[str, Any]:
        """Extract comprehensive financial data from annual report text"""
        
        # Llama 3.3 70B has 128k context, use up to 100k for text
        max_chars = 100000
        
        if len(text_content) > max_chars:
            print(f"📊 Calling Groq AI to extract financial data for {company_name}...")
            print(f"📄 Text length: {len(text_content):,} characters (using first {max_chars:,})")
            text_to_send = text_content[:max_chars]
        else:
            print(f"📊 Calling Groq AI to extract financial data for {company_name}...")
            print(f"📄 Text length: {len(text_content):,} characters (sending full document)")
            text_to_send = text_content
        
        # Create comprehensive prompt
        system_prompt = self.create_comprehensive_extraction_prompt(company_name)
        user_prompt = f"ANNUAL REPORT TEXT FOR {company_name.upper()}:\n\n{text_to_send}"
        
        print("🤖 Sending request to Groq API (this may take 30-90 seconds)...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert financial analyst specializing in comprehensive financial data extraction. You excel at reading complex financial documents and extracting detailed structured data."
                    },
                    {
                        "role": "user",
                        "content": system_prompt + "\n\n" + user_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for precise extraction
                max_tokens=16000,  # Increased for comprehensive response
                top_p=0.95
            )
            
            print("✅ Received response from Groq API")
            content = response.choices[0].message.content.strip()
            
            # Parse JSON from response
            print("📝 Parsing JSON response...")
            financial_data = self._parse_json_response(content)
            
            # Post-process and calculate derived metrics
            financial_data = self._calculate_derived_metrics(financial_data)
            
            print(f"✅ Successfully extracted comprehensive financial data")
            print(f"   📊 Top-level keys: {list(financial_data.keys())}")
            
            return financial_data
            
        except Exception as e:
            print(f"❌ Error during extraction: {str(e)}")
            # Return a minimal valid structure to avoid breaking the pipeline
            return {
                "metadata": {
                    "company_name": company_name,
                    "extraction_error": str(e),
                    "extraction_status": "failed"
                },
                "financial_statements": {},
                "financial_ratios": {},
                "segment_analysis": [],
                "geographic_analysis": []
            }
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response with multiple fallback strategies"""
        try:
            # Strategy 1: Direct parsing
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                # Strategy 2: Remove markdown code blocks
                if "```" in content:
                    # Extract content between ```json and ```
                    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                
                # Strategy 3: Find JSON object pattern
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                raise ValueError("No valid JSON found in response")
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed: {e}")
                print(f"Response preview: {content[:500]}...")
                raise ValueError(f"Failed to parse JSON from AI response: {e}")
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional metrics from extracted data"""
        try:
            financial_statements = data.get('financial_statements', {})
            income_current = financial_statements.get('income_statement', {}).get('current_year', {})
            balance_current = financial_statements.get('balance_sheet', {}).get('current_year', {})
            cash_flow_current = financial_statements.get('cash_flow', {}).get('current_year', {})
            
            if 'financial_ratios' not in data:
                data['financial_ratios'] = {}
            
            ratios = data['financial_ratios']
            
            # Profitability ratios
            revenue = income_current.get('revenue')
            net_income = income_current.get('net_income')
            gross_profit = income_current.get('gross_profit')
            operating_income = income_current.get('operating_income')
            
            if revenue and revenue > 0:
                if not ratios.get('gross_margin') and gross_profit:
                    ratios['gross_margin'] = round((gross_profit / revenue) * 100, 2)
                if not ratios.get('operating_margin') and operating_income:
                    ratios['operating_margin'] = round((operating_income / revenue) * 100, 2)
                if not ratios.get('net_profit_margin') and net_income:
                    ratios['net_profit_margin'] = round((net_income / revenue) * 100, 2)
            
            # Leverage ratios
            total_assets = balance_current.get('total_assets')
            total_liabilities = balance_current.get('total_liabilities')
            shareholders_equity = balance_current.get('total_shareholders_equity')
            
            if shareholders_equity and shareholders_equity > 0:
                if not ratios.get('debt_to_equity') and total_liabilities:
                    ratios['debt_to_equity'] = round(total_liabilities / shareholders_equity, 2)
                if not ratios.get('roe') and net_income:
                    ratios['roe'] = round((net_income / shareholders_equity) * 100, 2)
            
            if total_assets and total_assets > 0:
                if not ratios.get('roa') and net_income:
                    ratios['roa'] = round((net_income / total_assets) * 100, 2)
                if not ratios.get('debt_to_assets') and total_liabilities:
                    ratios['debt_to_assets'] = round(total_liabilities / total_assets, 2)
            
            # Liquidity ratios
            current_assets = balance_current.get('total_current_assets')
            current_liabilities = balance_current.get('total_current_liabilities')
            
            if current_liabilities and current_liabilities > 0 and current_assets:
                if not ratios.get('current_ratio'):
                    ratios['current_ratio'] = round(current_assets / current_liabilities, 2)
            
            # Free cash flow
            operating_cf = cash_flow_current.get('net_cash_from_operating_activities')
            capex = cash_flow_current.get('capital_expenditures')
            
            if not cash_flow_current.get('free_cash_flow') and operating_cf and capex:
                cash_flow_current['free_cash_flow'] = operating_cf - abs(capex)
            
            print("✅ Calculated derived metrics")
            
        except Exception as e:
            print(f"⚠️  Warning: Error calculating derived metrics: {str(e)}")
        
        return data
    
    def chat_completion(self, messages: List[Dict[str, str]], context: str = None, temperature: float = 0.7, max_tokens: int = 1500) -> str:
        """General chat completion for chatbot"""
        
        if context:
            messages.insert(0, {
                "role": "system",
                "content": f"Context: {context}\n\nAnswer questions based on this financial data."
            })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def code_generation(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 2000) -> str:
        """
        Code generation using Qwen2.5-Coder model optimized for agentic tasks
        
        Args:
            messages: List of message dicts with role and content
            temperature: Lower = more deterministic (0.1 best for code)
            max_tokens: Maximum response length
            
        Returns:
            Generated code as string
        """
        response = self.client.chat.completions.create(
            model=self.code_model,  # Use Qwen for code generation
            messages=messages,
            temperature=temperature,  # Lower temperature for more accurate code
            max_tokens=max_tokens
        )
        
                
        return response.choices[0].message.content

groq_client = GroqClient()
