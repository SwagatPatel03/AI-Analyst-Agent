"""
Google Gemini AI client for comprehensive financial data extraction
"""
import google.generativeai as genai
from app.config import settings
from typing import Optional, Dict, Any, List
import json
import re


class GeminiClient:
    """Client for Google Gemini API with advanced financial extraction"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use gemini-2.0-flash for better performance
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def chunk_text(self, text: str, max_chunk_size: int = 40000) -> List[str]:
        """Split text into chunks for processing"""
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs to maintain context
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > max_chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [text]
    
    def create_comprehensive_extraction_prompt(self, company_name: str, is_first_chunk: bool = True) -> str:
        """Create comprehensive extraction prompt"""
        
        if is_first_chunk:
            return f"""You are an expert financial analyst with deep expertise in analyzing annual reports, 10-K filings, and financial statements.

Your task: Extract COMPREHENSIVE financial data from the {company_name} annual report text below.

EXTRACT ALL OF THE FOLLOWING (use null if not found):

1. COMPANY METADATA:
   - company_name, fiscal_year, reporting_period_start, reporting_period_end
   - currency, fiscal_quarter, auditor_name, auditor_opinion, report_date

2. INCOME STATEMENT (Current Year & Previous Year):
   - revenue, cost_of_revenue, gross_profit
   - research_and_development, sales_and_marketing, general_and_administrative
   - total_operating_expenses, operating_income, operating_margin
   - interest_income, interest_expense, other_income_expense
   - income_before_tax, income_tax_expense, effective_tax_rate
   - net_income, net_income_margin, basic_eps, diluted_eps
   - weighted_average_shares_basic, weighted_average_shares_diluted
   - ebitda, ebit

3. BALANCE SHEET (Current Year & Previous Year):
   ASSETS:
   - cash_and_cash_equivalents, short_term_investments, marketable_securities
   - accounts_receivable, inventory, prepaid_expenses, other_current_assets
   - total_current_assets
   - property_plant_equipment_gross, accumulated_depreciation, property_plant_equipment_net
   - intangible_assets, goodwill, long_term_investments, other_non_current_assets
   - total_non_current_assets, total_assets
   
   LIABILITIES:
   - accounts_payable, accrued_expenses, short_term_debt, deferred_revenue_current
   - current_portion_long_term_debt, other_current_liabilities, total_current_liabilities
   - long_term_debt, deferred_tax_liabilities, deferred_revenue_non_current
   - other_long_term_liabilities, total_non_current_liabilities, total_liabilities
   
   EQUITY:
   - common_stock, preferred_stock, additional_paid_in_capital, retained_earnings
   - treasury_stock, accumulated_other_comprehensive_income, total_shareholders_equity

4. CASH FLOW STATEMENT (Current Year & Previous Year):
   OPERATING:
   - net_income_cf, depreciation_amortization, stock_based_compensation
   - deferred_income_taxes, changes_in_working_capital, other_operating_activities
   - net_cash_from_operating_activities
   
   INVESTING:
   - capital_expenditures, acquisitions, purchases_of_investments, sales_of_investments
   - other_investing_activities, net_cash_from_investing_activities
   
   FINANCING:
   - proceeds_from_debt, repayment_of_debt, dividends_paid, stock_repurchases
   - proceeds_from_stock_issuance, other_financing_activities
   - net_cash_from_financing_activities
   
   - net_change_in_cash, cash_beginning_of_period, cash_end_of_period
   - free_cash_flow

5. KEY PERFORMANCE INDICATORS:
   PROFITABILITY: gross_margin, operating_margin, net_profit_margin, roe, roa, roic
   LIQUIDITY: current_ratio, quick_ratio, cash_ratio, working_capital
   LEVERAGE: debt_to_equity, debt_to_assets, interest_coverage
   EFFICIENCY: asset_turnover, inventory_turnover, receivables_turnover
   VALUATION: pe_ratio, price_to_book, price_to_sales, ev_to_ebitda, market_cap
   GROWTH: revenue_growth_yoy, net_income_growth_yoy, eps_growth_yoy
   PER SHARE: book_value_per_share, revenue_per_share, cash_per_share

6. BUSINESS SEGMENTS (array):
   For each segment: segment_name, revenue_current, revenue_previous,
   operating_income_current, operating_income_previous, segment_margin, segment_assets

7. GEOGRAPHIC BREAKDOWN (array):
   For each region: region_name, revenue_current, revenue_previous,
   operating_income, percentage_of_total

8. MANAGEMENT DISCUSSION & ANALYSIS:
   - business_overview, key_strategies, competitive_position
   - market_opportunities, key_risks, management_outlook
   - significant_events, regulatory_matters

9. OPERATIONAL METRICS:
   - employee_count, employee_growth_rate
   - customer_count, active_users, subscriber_count
   - average_revenue_per_user, customer_acquisition_cost
   - store_count, production_volume, capacity_utilization

10. SHAREHOLDER RETURNS:
    - dividend_per_share, dividend_yield, dividend_payout_ratio
    - total_dividends_paid, share_repurchases, total_shareholder_return

11. ESG & SUSTAINABILITY:
    - carbon_emissions, renewable_energy_percentage
    - diversity_metrics, board_diversity, esg_initiatives

12. CEO LETTER / EXECUTIVE SUMMARY:
    - ceo_statement_summary (key themes and messages)

CRITICAL RULES:
✓ Extract ACTUAL NUMBERS from financial statements
✓ Report amounts in MILLIONS (e.g., $245 billion = 245000)
✓ Include BOTH current and previous year data where available
✓ Use null if value not found (DO NOT guess or make up data)
✓ Calculate year-over-year growth rates where possible
✓ Use proper data types: numbers for values, strings for text, arrays for lists

RESPONSE FORMAT - Return ONLY valid JSON (no markdown, no explanations):
{{
  "metadata": {{
    "company_name": "string",
    "fiscal_year": number,
    "reporting_period_start": "YYYY-MM-DD",
    "reporting_period_end": "YYYY-MM-DD",
    "currency": "USD",
    "auditor_name": "string"
  }},
  "financial_statements": {{
    "income_statement": {{
      "current_year": {{...all income statement items...}},
      "previous_year": {{...}}
    }},
    "balance_sheet": {{
      "current_year": {{...all balance sheet items...}},
      "previous_year": {{...}}
    }},
    "cash_flow": {{
      "current_year": {{...all cash flow items...}},
      "previous_year": {{...}}
    }}
  }},
  "financial_ratios": {{...all ratios...}},
  "segment_analysis": [...array of segments...],
  "geographic_analysis": [...array of regions...],
  "management_analysis": {{...}},
  "operational_metrics": {{...}},
  "shareholder_returns": {{...}},
  "esg_data": {{...}},
  "ceo_statement_summary": "string"
}}

ANNUAL REPORT TEXT:
"""
        else:
            return f"""Continue extracting financial data from this additional section of the {company_name} annual report.

SUPPLEMENT the previous extraction with any NEW data found here. Focus on:
- Additional financial statement line items not yet captured
- More segment or geographic details
- Additional operational metrics
- More detailed MD&A insights
- Any missing KPIs or ratios

Return ONLY new/additional data in the same JSON format. Use null if nothing new found.

ADDITIONAL TEXT:
"""
    
    def extract_financial_data(self, text_content: str, company_name: str) -> Dict[str, Any]:
        """Extract comprehensive financial data using multi-pass approach"""
        
        print(f"📊 Starting Gemini AI extraction for {company_name}...")
        print(f"📄 Document length: {len(text_content):,} characters")
        
        # Chunk the text
        chunks = self.chunk_text(text_content, max_chunk_size=40000)
        print(f"📑 Split into {len(chunks)} chunks for processing")
        
        # Process first chunk with full extraction
        print(f"🔍 Processing chunk 1/{len(chunks)} (primary extraction)...")
        first_prompt = self.create_comprehensive_extraction_prompt(company_name, is_first_chunk=True)
        
        try:
            response1 = self.model.generate_content(
                first_prompt + "\n\n" + chunks[0],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 8192,
                }
            )
            
            financial_data = self._parse_json_response(response1.text)
            print(f"✅ Extracted data from chunk 1")
            
            # Process additional chunks if they exist
            if len(chunks) > 1:
                supplement_prompt = self.create_comprehensive_extraction_prompt(company_name, is_first_chunk=False)
                
                for i, chunk in enumerate(chunks[1:], start=2):
                    print(f"🔍 Processing chunk {i}/{len(chunks)} (supplemental)...")
                    
                    try:
                        response = self.model.generate_content(
                            supplement_prompt + "\n\n" + chunk,
                            generation_config={
                                "temperature": 0.1,
                                "max_output_tokens": 4096,
                            }
                        )
                        
                        supplement_data = self._parse_json_response(response.text)
                        financial_data = self._merge_dicts(financial_data, supplement_data)
                        print(f"✅ Merged data from chunk {i}")
                        
                    except Exception as e:
                        print(f"⚠️  Warning: Chunk {i} processing failed: {str(e)}")
                        continue
            
            # Calculate derived metrics
            financial_data = self._calculate_derived_metrics(financial_data)
            
            print(f"✅ Extraction complete!")
            print(f"   📊 Top-level keys: {list(financial_data.keys())}")
            
            return financial_data
            
        except Exception as e:
            print(f"❌ Extraction error: {str(e)}")
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
        """Parse JSON from AI response"""
        try:
            # Remove markdown code blocks
            if "```" in content:
                json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            # Try direct parsing
            return json.loads(content)
            
        except json.JSONDecodeError:
            # Try finding JSON object
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            raise ValueError(f"Failed to parse JSON from response")
    
    def _merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dicts(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key].extend(value)
                elif value is not None:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional financial metrics"""
        try:
            fs = data.get('financial_statements', {})
            income = fs.get('income_statement', {}).get('current_year', {})
            balance = fs.get('balance_sheet', {}).get('current_year', {})
            cash_flow = fs.get('cash_flow', {}).get('current_year', {})
            
            if 'financial_ratios' not in data:
                data['financial_ratios'] = {}
            
            ratios = data['financial_ratios']
            
            # Profitability ratios
            revenue = income.get('revenue')
            net_income = income.get('net_income')
            gross_profit = income.get('gross_profit')
            operating_income = income.get('operating_income')
            
            if revenue and revenue > 0:
                if not ratios.get('gross_margin') and gross_profit:
                    ratios['gross_margin'] = round((gross_profit / revenue) * 100, 2)
                if not ratios.get('operating_margin') and operating_income:
                    ratios['operating_margin'] = round((operating_income / revenue) * 100, 2)
                if not ratios.get('net_profit_margin') and net_income:
                    ratios['net_profit_margin'] = round((net_income / revenue) * 100, 2)
            
            # Return ratios
            total_assets = balance.get('total_assets')
            shareholders_equity = balance.get('total_shareholders_equity')
            
            if shareholders_equity and shareholders_equity > 0 and net_income:
                if not ratios.get('roe'):
                    ratios['roe'] = round((net_income / shareholders_equity) * 100, 2)
            
            if total_assets and total_assets > 0 and net_income:
                if not ratios.get('roa'):
                    ratios['roa'] = round((net_income / total_assets) * 100, 2)
            
            # Leverage ratios
            total_liabilities = balance.get('total_liabilities')
            
            if shareholders_equity and shareholders_equity > 0 and total_liabilities:
                if not ratios.get('debt_to_equity'):
                    ratios['debt_to_equity'] = round(total_liabilities / shareholders_equity, 2)
            
            # Liquidity ratios
            current_assets = balance.get('total_current_assets')
            current_liabilities = balance.get('total_current_liabilities')
            
            if current_liabilities and current_liabilities > 0:
                if current_assets and not ratios.get('current_ratio'):
                    ratios['current_ratio'] = round(current_assets / current_liabilities, 2)
            
            # Free cash flow
            operating_cf = cash_flow.get('net_cash_from_operating_activities')
            capex = cash_flow.get('capital_expenditures')
            
            if operating_cf and capex and not cash_flow.get('free_cash_flow'):
                cash_flow['free_cash_flow'] = operating_cf - abs(capex)
            
            print("✅ Calculated derived metrics")
            
        except Exception as e:
            print(f"⚠️  Warning: Error calculating metrics: {str(e)}")
        
        return data
    
    def extract_ml_ready_data(self, text_content: str, company_name: str) -> Dict[str, Any]:
        """
        Extract ML-ready financial data in the exact format required by ML predictor.
        This creates a simplified, focused extraction optimized for ML predictions.
        
        Returns data in format:
        {
            "company_name": str,
            "revenue": float,
            "revenue_history": [float, float],  # 2 years minimum
            "net_income": float,
            "net_income_history": [float, float],  # 2 years minimum
            "total_assets": float,
            "total_liabilities": float,
            "shareholders_equity": float,
            "key_metrics": {
                "eps": float,
                "pe_ratio": float,
                "roe": float,
                "debt_to_equity": float,
                "current_ratio": float,
                "profit_margin": float,
                "operating_margin": float,
                "quick_ratio": float
            }
        }
        """
        
        print(f"\n🎯 Extracting ML-ready data for {company_name}...")
        
        prompt = f"""You are an expert financial analyst. Extract ONLY the specific financial data needed for machine learning predictions from this {company_name} annual report.

CRITICAL: You MUST extract AT LEAST 2 YEARS of historical data for revenue and net income. This is REQUIRED for ML predictions.

Extract the following in EXACT JSON format:

{{
  "company_name": "{company_name}",
  "revenue": <current year total revenue as number>,
  "revenue_history": [<previous year revenue>, <current year revenue>],
  "net_income": <current year net income as number>,
  "net_income_history": [<previous year net income>, <current year net income>],
  "total_assets": <total assets as number>,
  "total_liabilities": <total liabilities as number>,
  "shareholders_equity": <shareholders equity as number>,
  "key_metrics": {{
    "eps": <earnings per share as number>,
    "pe_ratio": <price to earnings ratio as number>,
    "roe": <return on equity % as number>,
    "debt_to_equity": <debt to equity ratio as number>,
    "current_ratio": <current ratio as number>,
    "profit_margin": <profit margin % as number>,
    "operating_margin": <operating margin % as number>,
    "quick_ratio": <quick ratio as number>
  }}
}}

INSTRUCTIONS:
1. Extract numbers WITHOUT commas, dollar signs, or symbols (e.g., 1000000 not $1,000,000)
2. Convert all percentages to decimal numbers (e.g., 15.5 not 15.5%)
3. revenue_history and net_income_history MUST have at least 2 years of data [previous_year, current_year]
4. If a metric is not found, use null (not 0)
5. Return ONLY the JSON object, no explanations

ANNUAL REPORT TEXT:
{text_content[:50000]}
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Low temperature for accuracy
                    "max_output_tokens": 2048,
                }
            )
            
            ml_data = self._parse_json_response(response.text)
            
            # Validate required fields
            required_fields = ['company_name', 'revenue', 'revenue_history', 'net_income', 'net_income_history']
            missing_fields = [field for field in required_fields if not ml_data.get(field)]
            
            if missing_fields:
                print(f"⚠️ Warning: Missing required fields: {missing_fields}")
            
            # Validate history arrays
            if len(ml_data.get('revenue_history', [])) < 2:
                print(f"⚠️ Warning: revenue_history has less than 2 years of data")
            
            if len(ml_data.get('net_income_history', [])) < 2:
                print(f"⚠️ Warning: net_income_history has less than 2 years of data")
            
            print(f"✅ ML-ready data extracted successfully")
            print(f"   • Company: {ml_data.get('company_name')}")
            print(f"   • Revenue: ${ml_data.get('revenue', 0):,.0f}")
            print(f"   • Revenue History: {len(ml_data.get('revenue_history', []))} years")
            print(f"   • Net Income: ${ml_data.get('net_income', 0):,.0f}")
            print(f"   • Net Income History: {len(ml_data.get('net_income_history', []))} years")
            print(f"   • Key Metrics: {len(ml_data.get('key_metrics', {}))}")
            
            return ml_data
            
        except Exception as e:
            print(f"❌ Error extracting ML-ready data: {str(e)}")
            return {
                "company_name": company_name,
                "revenue": None,
                "revenue_history": [],
                "net_income": None,
                "net_income_history": [],
                "total_assets": None,
                "total_liabilities": None,
                "shareholders_equity": None,
                "key_metrics": {},
                "extraction_error": str(e)
            }
    
    async def generate(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat completion with message history
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response
        """
        try:
            chat = self.model.start_chat(history=[])
            
            # Add message history
            for msg in messages[:-1]:
                if msg['role'] == 'user':
                    chat.send_message(msg['content'])
            
            # Send final message and get response
            response = chat.send_message(messages[-1]['content'])
            
            return response.text
        
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_report(
        self,
        company_name: str,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any],
        visualizations: Optional[list] = None
    ) -> str:
        """
        Generate comprehensive financial analysis report
        
        Args:
            company_name: Company name
            financial_data: Extracted financial data
            predictions: ML predictions (basic or enhanced)
            visualizations: List of visualization paths (optional)
        
        Returns:
            Generated report as markdown
        
        Raises:
            Exception: If Gemini API is not configured or generation fails
        """
        
        # Build comprehensive prompt
        prompt = self._build_report_prompt(
            company_name,
            financial_data,
            predictions,
            visualizations or []
        )
        
        # Retry logic with exponential backoff
        import time
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Generate content with Gemini
                response = self.model.generate_content(prompt)
                
                if not response or not response.text:
                    raise Exception("Empty response from Gemini API")
                
                return response.text
            
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a retryable error (503, overloaded, timeout)
                is_retryable = any(keyword in error_msg.lower() for keyword in 
                                  ['503', 'overloaded', 'timeout', 'unavailable'])
                
                if is_retryable and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"  ⚠️  Gemini API busy (attempt {attempt + 1}/{max_retries}), retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                
                # If not retryable or final attempt, generate fallback report
                print(f"  ⚠️  Gemini API unavailable: {error_msg}")
                print(f"  🔄 Generating fallback report with available data...")
                return self._generate_fallback_report(company_name, financial_data, predictions)
        
        # Should never reach here, but just in case
        return self._generate_fallback_report(company_name, financial_data, predictions)
    
    def _build_report_prompt(
        self,
        company_name: str,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any],
        visualizations: list
    ) -> str:
        """
        Build comprehensive prompt for report generation
        
        Supports both basic and enhanced predictions
        """
        
        # Extract financial data
        revenue = financial_data.get('revenue', {})
        net_income = financial_data.get('net_income', {})
        metrics = financial_data.get('key_metrics', {})
        
        # Handle both dict and direct values
        revenue_current = revenue.get('current_year') if isinstance(revenue, dict) else revenue
        revenue_previous = revenue.get('previous_year') if isinstance(revenue, dict) else 0
        net_income_current = net_income.get('current_year') if isinstance(net_income, dict) else net_income
        net_income_previous = net_income.get('previous_year') if isinstance(net_income, dict) else 0
        
        # Currency
        currency = revenue.get('currency', 'USD') if isinstance(revenue, dict) else 'USD'
        
        # Build improved, data-driven prompt
        prompt = f"""
You are an expert financial analyst. Using the following structured JSON data for {company_name}, generate a comprehensive, professional financial analysis report. Use actual numbers and facts from the data. Do NOT use generic templates or boilerplate. If a field is missing, skip it.

## JSON Data (for reference):
```
{financial_data}
```

## Required Sections:
1. **Executive Summary** (2-3 concise, business-style paragraphs)
   - Summarize key financials (revenue, net income, growth rates, margins, ROE, etc.)
   - Highlight segment and geographic performance
   - Mention shareholder returns, management outlook, and ESG if available
   - Use clear, non-generic language and cite specific numbers
2. **Financial Performance Analysis**
3. **Key Metrics Interpretation**
4. **Growth Predictions and Forecast**
5. **Risk Assessment**
6. **Performance Evaluation** (if data available)
7. **Market Position** (if data available)
8. **Investment Recommendations**
9. **Conclusion**

## Formatting Guidelines:
- Use markdown formatting
- Include tables for numerical data
- Use bullet points for lists
- Emphasize important points with **bold**
- Keep language professional and clear
- Target length: 1500-2000 words
- Use section headers (#, ##, ###)
- Include data-driven insights
- Cite specific numbers from the data provided

## Tone and Style:
- Professional and analytical
- Data-driven and objective
- Clear and concise
- Suitable for investors and stakeholders
- Balance technical detail with readability

Generate the report now:
"""
        return prompt
        
        return prompt
    
    def _format_sales_forecast(self, forecast: list) -> str:
        """Format sales forecast for prompt"""
        if not forecast:
            return "No forecast available"
        
        formatted = []
        for pred in forecast:
            year = pred.get('year', 'N/A')
            revenue = pred.get('predicted_revenue', 0)
            currency = pred.get('currency', 'USD')
            growth = pred.get('growth_rate', 0)
            
            line = f"- **Year {year}**: {revenue:,.2f} {currency}"
            
            # Add confidence bounds if available
            if pred.get('confidence_lower') and pred.get('confidence_upper'):
                lower = pred.get('confidence_lower')
                upper = pred.get('confidence_upper')
                line += f" (Range: {lower:,.2f} - {upper:,.2f} {currency})"
            
            line += f" | Growth: {growth}%"
            
            formatted.append(line)
        
        return "\n".join(formatted)
    
    def _format_scenarios(self, scenarios: Dict[str, Any]) -> str:
        """Format scenario analysis for prompt"""
        formatted = []
        
        for scenario_name, scenario_data in scenarios.items():
            name = scenario_name.replace('_', ' ').title()
            formatted.append(f"\n### {name}")
            formatted.append(f"- Growth Rate: {scenario_data.get('growth_rate')}%")
            formatted.append(f"- Probability: {scenario_data.get('probability', 0) * 100}%")
            formatted.append(f"- Description: {scenario_data.get('description')}")
            
            # Add key assumptions
            assumptions = scenario_data.get('key_assumptions', [])
            if assumptions:
                formatted.append("- Key Assumptions:")
                for assumption in assumptions:
                    formatted.append(f"  - {assumption}")
        
        return "\n".join(formatted)
    
    def _format_recommendations(self, recommendations: list) -> str:
        """Format investment recommendations for prompt"""
        if not recommendations:
            return "No specific recommendations available"
        
        formatted = []
        
        # Check if enhanced format (with structured data)
        if recommendations and isinstance(recommendations[0], dict):
            for rec in recommendations:
                category = rec.get('category', 'General')
                title = rec.get('title', '')
                description = rec.get('description', '')
                action = rec.get('action', '')
                priority = rec.get('priority', '')
                
                formatted.append(f"\n### {title} ({category})")
                if description:
                    formatted.append(f"- **Analysis**: {description}")
                if action:
                    formatted.append(f"- **Action**: {action}")
                if priority:
                    formatted.append(f"- **Priority**: {priority}")
        else:
            # Simple format
            formatted = [f"- {rec}" for rec in recommendations]
        
        return "\n".join(formatted)
    
    def _format_segments(self, segments: list) -> str:
        """Format segment breakdown for prompt"""
        if not segments:
            return "No segment data available"
        
        formatted = []
        for segment in segments:
            name = segment.get('segment', 'Unknown')
            current = segment.get('current_revenue', 0)
            predicted = segment.get('predicted_revenue', 0)
            growth = segment.get('predicted_growth', 0)
            proportion = segment.get('proportion', 0)
            
            formatted.append(f"\n### {name}")
            formatted.append(f"- Current Revenue: {current:,.2f} ({proportion}% of total)")
            formatted.append(f"- Predicted Revenue: {predicted:,.2f}")
            formatted.append(f"- Predicted Growth: {growth}%")
            
            # Add growth driver if available
            if segment.get('growth_driver'):
                formatted.append(f"- Growth Driver: {segment.get('growth_driver')}")
        
        return "\n".join(formatted)
    
    def _generate_fallback_report(
        self,
        company_name: str,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> str:
        """
        Generate a basic report when Gemini API is unavailable
        Uses templates and available data to create a comprehensive report
        """
        from datetime import datetime
        
        # Extract key metrics
        revenue = financial_data.get('revenue', 0)
        net_income = financial_data.get('net_income', 0)
        growth_rate = predictions.get('predicted_growth_rate', 0)
        
        # Get enhanced features if available
        sales_forecast = predictions.get('sales_forecast', {})
        scenarios = predictions.get('scenario_analysis', {})
        risk_metrics = predictions.get('risk_assessment', {})
        performance = predictions.get('performance_metrics', {})
        industry_comp = predictions.get('industry_comparison', {})
        
        # Build report sections
        report = f"""# Financial Analysis Report: {company_name}

**Generated:** {datetime.now().strftime('%B %d, %Y')}  
**Status:** Automated Report (Gemini AI unavailable)

---

## Executive Summary

{company_name} demonstrates {"strong" if growth_rate > 15 else "moderate" if growth_rate > 5 else "stable"} financial performance with a current revenue of ${revenue:,.0f} and net income of ${net_income:,.0f}. Our ML-powered analysis projects a growth rate of **{growth_rate:.2f}%** for the coming year.

### Key Highlights

- **Current Revenue:** ${revenue:,.0f}
- **Net Income:** ${net_income:,.0f}
- **Projected Growth Rate:** {growth_rate:.2f}%
- **Profit Margin:** {(net_income/revenue*100):.2f}%

---

## Financial Performance Analysis

### Revenue Growth Trajectory

Based on historical data and advanced ML models (Linear Regression, Random Forest, Gradient Boosting), we project a **{growth_rate:.2f}% growth rate** for {company_name}.

"""

        # Add sales forecast if available
        if sales_forecast and sales_forecast.get('forecast'):
            report += "### Multi-Year Sales Forecast\n\n"
            report += "| Year | Projected Revenue | Growth Rate |\n"
            report += "|------|------------------|-------------|\n"
            
            for year_data in sales_forecast['forecast'][:5]:
                year = year_data.get('year', 'N/A')
                projected = year_data.get('projected_sales', 0)
                growth = year_data.get('growth_rate', growth_rate)
                report += f"| {year} | ${projected:,.0f} | {growth:.2f}% |\n"
            
            report += "\n"
        
        # Add scenario analysis if available
        if scenarios and scenarios.get('scenarios'):
            report += "### Scenario Analysis\n\n"
            report += "Our Monte Carlo simulation (1,000 iterations) provides the following scenarios:\n\n"
            
            for scenario in scenarios['scenarios']:
                scenario_type = scenario.get('scenario', 'Unknown')
                growth = scenario.get('growth_rate', 0)
                probability = scenario.get('probability', 0)
                report += f"- **{scenario_type} Case:** {growth:.2f}% growth (Probability: {probability:.0f}%)\n"
            
            report += "\n"
        
        # Add risk assessment if available
        if risk_metrics:
            report += "### Risk Assessment\n\n"
            
            risk_level = risk_metrics.get('risk_level', 'Unknown')
            risk_score = risk_metrics.get('risk_score', 0)
            health_score = risk_metrics.get('financial_health_score', 0)
            
            report += f"- **Risk Level:** {risk_level}\n"
            report += f"- **Risk Score:** {risk_score}/100\n"
            report += f"- **Financial Health:** {health_score}/100\n"
            
            if risk_metrics.get('value_at_risk_95'):
                var = risk_metrics['value_at_risk_95']
                report += f"- **Value at Risk (95%):** ${var:,.0f}\n"
            
            report += "\n"
        
        # Add performance metrics if available
        if performance:
            report += "### Performance Metrics\n\n"
            
            if performance.get('historical_cagr'):
                report += f"- **Historical CAGR:** {performance['historical_cagr']:.2f}%\n"
            if performance.get('projected_cagr_3y'):
                report += f"- **Projected 3-Year CAGR:** {performance['projected_cagr_3y']:.2f}%\n"
            if performance.get('roic'):
                report += f"- **Return on Invested Capital (ROIC):** {performance['roic']:.2f}%\n"
            if performance.get('roa'):
                report += f"- **Return on Assets (ROA):** {performance['roa']:.2f}%\n"
            if performance.get('efficiency_score'):
                report += f"- **Efficiency Score:** {performance['efficiency_score']}/100\n"
            
            report += "\n"
        
        # Add industry comparison if available
        if industry_comp:
            report += "### Industry Position\n\n"
            
            position = industry_comp.get('competitive_position', 'N/A')
            report += f"{company_name} holds a **{position}** position in its industry.\n\n"
            
            if industry_comp.get('outperforming_metrics'):
                count = industry_comp['outperforming_metrics']
                total = industry_comp.get('total_metrics', 4)
                report += f"- Outperforming on {count}/{total} key metrics\n"
            
            report += "\n"
        
        # Add market conditions
        market_conditions = predictions.get('market_conditions', {})
        if market_conditions:
            report += "### Market Conditions\n\n"
            
            phase = market_conditions.get('market_phase', 'N/A')
            outlook = market_conditions.get('outlook', 'N/A')
            
            report += f"- **Current Phase:** {phase}\n"
            report += f"- **Outlook:** {outlook}\n\n"
        
        # Add recommendations
        recommendations = predictions.get('investment_recommendations', [])
        if recommendations:
            report += "## Investment Recommendations\n\n"
            
            if isinstance(recommendations, list):
                for i, rec in enumerate(recommendations[:5], 1):
                    if isinstance(rec, dict):
                        rec_type = rec.get('type', 'General')
                        category = rec.get('category', '')
                        recommendation = rec.get('recommendation', '')
                        impact = rec.get('impact', '')
                        
                        report += f"### {i}. {rec_type}\n\n"
                        if category:
                            report += f"**Category:** {category}\n\n"
                        if recommendation:
                            report += f"{recommendation}\n\n"
                        if impact:
                            report += f"**Expected Impact:** {impact}\n\n"
                    else:
                        report += f"{i}. {rec}\n"
            
            report += "\n"
        
        # Add conclusion
        report += """---

## Conclusion

This automated analysis provides a comprehensive overview of the company's financial position and future prospects. The projections are based on ensemble machine learning models and statistical analysis of historical data.

### Key Takeaways

"""
        
        if growth_rate > 15:
            report += "- Strong growth trajectory indicating robust business expansion\n"
        elif growth_rate > 5:
            report += "- Steady growth trajectory indicating stable business performance\n"
        else:
            report += "- Conservative growth trajectory suggesting market maturity\n"
        
        if risk_metrics and risk_metrics.get('risk_level', '').lower() == 'low':
            report += "- Low risk profile provides favorable conditions for investment\n"
        
        if performance and performance.get('efficiency_score', 0) > 80:
            report += "- High efficiency score demonstrates strong operational excellence\n"
        
        report += """
---

**Disclaimer:** This report was automatically generated using machine learning algorithms. While our models are highly accurate, all investment decisions should be made in consultation with qualified financial advisors. Past performance does not guarantee future results.

**Data Sources:** Company financial statements, market data, and proprietary ML models.

**Methodology:** Ensemble ML (Linear Regression, Random Forest, Gradient Boosting), Monte Carlo Simulation (1,000 iterations), Statistical Analysis.
"""
        
        return report
    
    def generate_visualizations(
        self,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any],
        company_name: str,
        report_id: int
    ) -> List[str]:
        """
        Generate intelligent visualizations using Gemini AI
        
        Args:
            financial_data: Complete financial data dictionary
            predictions: ML prediction results
            company_name: Name of the company
            report_id: ID for the report (used for file naming)
            
        Returns:
            List of file paths to generated visualization PNGs
        """
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        import os
        from pathlib import Path
        
        try:
            print(f"  🎨 Asking Gemini AI for visualization suggestions...")
            
            # Build the prompt for Gemini
            viz_prompt = self._build_visualization_prompt(financial_data, predictions, company_name)
            
            try:
                # Ask Gemini for visualization suggestions
                response = self.model.generate_content(
                    viz_prompt,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 4096,
                    }
                )
                
                # Parse the response to get chart specifications
                chart_specs = self._parse_visualization_response(response.text)
                print(f"  ✅ Gemini suggested {len(chart_specs)} visualizations")
                
            except Exception as e:
                print(f"  ⚠️  Gemini visualization request failed: {str(e)}")
                print(f"  📊 Using fallback visualizations...")
                chart_specs = self._generate_fallback_chart_specs(financial_data, predictions, company_name)
        except Exception as e:
            print(f"  ❌ Visualization generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        
        # Generate the charts
        viz_paths = []
        outputs_dir = Path("outputs/reports")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        
        for i, spec in enumerate(chart_specs, 1):
            try:
                chart_path = self._generate_chart(spec, report_id, company_name, i)
                if chart_path:
                    viz_paths.append(chart_path)
                    file_size = os.path.getsize(chart_path) / 1024
                    print(f"  ✅ Generated: {Path(chart_path).name} ({file_size:.1f} KB)")
            except Exception as e:
                print(f"  ⚠️  Chart {i} generation failed: {str(e)}")
                continue
        
        return viz_paths
    
    def _build_visualization_prompt(
        self,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any],
        company_name: str
    ) -> str:
        """Build a comprehensive prompt for Gemini to suggest visualizations"""
        
        prompt = f"""You are a data visualization expert analyzing financial data for {company_name}.

# AVAILABLE DATA:

## Financial Metrics:
"""
        
        # Handle different financial data structures
        if isinstance(financial_data, list):
            # If it's a list, try to get the first item
            financial_data = financial_data[0] if financial_data else {}
        
        # Try to extract key metrics from different possible structures
        # Structure 1: Direct fields (test data format)
        if 'revenue' in financial_data:
            prompt += f"\n- Revenue: ${financial_data.get('revenue', 0):,.0f}"
        if 'net_income' in financial_data:
            prompt += f"\n- Net Income: ${financial_data.get('net_income', 0):,.0f}"
        if 'total_assets' in financial_data:
            prompt += f"\n- Total Assets: ${financial_data.get('total_assets', 0):,.0f}"
        if 'total_liabilities' in financial_data:
            prompt += f"\n- Total Liabilities: ${financial_data.get('total_liabilities', 0):,.0f}"
        if 'shareholders_equity' in financial_data:
            prompt += f"\n- Shareholders Equity: ${financial_data.get('shareholders_equity', 0):,.0f}"
        
        # Structure 2: Nested financial_statements (extracted data format)
        financial_statements = financial_data.get('financial_statements', {})
        if financial_statements:
            income_statement = financial_statements.get('income_statement', {})
            balance_sheet = financial_statements.get('balance_sheet', {})
            
            if income_statement:
                if 'revenue' in income_statement:
                    revenue_val = income_statement['revenue']
                    if isinstance(revenue_val, dict):
                        prompt += f"\n- Revenue: {revenue_val.get('current_year', 'N/A')}"
                if 'net_income' in income_statement:
                    ni_val = income_statement['net_income']
                    if isinstance(ni_val, dict):
                        prompt += f"\n- Net Income: {ni_val.get('current_year', 'N/A')}"
            
            if balance_sheet:
                if 'total_assets' in balance_sheet:
                    ta_val = balance_sheet['total_assets']
                    if isinstance(ta_val, dict):
                        prompt += f"\n- Total Assets: {ta_val.get('current_year', 'N/A')}"
        
        # Add prediction data
        prompt += f"""

## ML Predictions:
- Projected Growth Rate: {predictions.get('growth_rate', 'N/A')}%
- Confidence Interval: {predictions.get('confidence_interval', {})}
"""
        
        # Handle sales_forecast (could be list or dict)
        if predictions.get('sales_forecast'):
            sales_forecast = predictions['sales_forecast']
            if isinstance(sales_forecast, list):
                forecast_count = len(sales_forecast)
            elif isinstance(sales_forecast, dict):
                forecast_count = len(sales_forecast.get('forecast', []))
            else:
                forecast_count = 0
            
            if forecast_count > 0:
                prompt += f"- Sales Forecast: {forecast_count} years available\n"
        
        # Handle scenarios (could be dict or nested dict)
        scenarios_data = predictions.get('scenarios', predictions.get('scenario_analysis'))
        if scenarios_data:
            if isinstance(scenarios_data, dict):
                if 'scenarios' in scenarios_data:
                    scenario_count = len(scenarios_data['scenarios'])
                else:
                    scenario_count = len(scenarios_data)
            elif isinstance(scenarios_data, list):
                scenario_count = len(scenarios_data)
            else:
                scenario_count = 0
            
            if scenario_count > 0:
                prompt += f"- Scenario Analysis: {scenario_count} scenarios (Best/Base/Worst case)\n"
        
        # Handle risk assessment
        risk_data = predictions.get('risk_metrics', predictions.get('risk_assessment'))
        if risk_data:
            prompt += f"- Risk Level: {risk_data.get('risk_level', 'N/A')}\n"
            prompt += f"- Financial Health Score: {risk_data.get('financial_health_score', 'N/A')}/100\n"
        
        prompt += """

# YOUR TASK:

Analyze this financial data and suggest 4-5 impactful visualizations that would best communicate the company's financial story.

For each visualization, specify:
1. chart_type: "bar", "line", "pie", "scatter", "stacked_bar", or "horizontal_bar"
2. title: Clear, descriptive title
3. data: The specific data to visualize (with labels and values)
4. x_label: X-axis label (if applicable)
5. y_label: Y-axis label (if applicable)
6. insights: Brief insight about what this chart reveals

Return ONLY a JSON array in this exact format:
```json
[
  {
    "chart_type": "bar",
    "title": "Revenue Growth Trend",
    "data": {
      "labels": ["2022", "2023", "2024"],
      "values": [100000, 120000, 145000]
    },
    "x_label": "Year",
    "y_label": "Revenue ($)",
    "insights": "Consistent year-over-year revenue growth"
  }
]
```

IMPORTANT:
- Use REAL data from above (extract exact values)
- Choose chart types that best represent each metric
- Prioritize the most impactful metrics
- Keep insights concise and actionable
"""
        
        return prompt
    
    def _parse_visualization_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Gemini's visualization suggestions from JSON response"""
        
        try:
            # Remove markdown code blocks if present
            content = response_text
            if "```" in content:
                json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            # Parse JSON
            chart_specs = json.loads(content)
            
            # Validate it's a list
            if not isinstance(chart_specs, list):
                raise ValueError("Response is not a list of chart specifications")
            
            return chart_specs
            
        except Exception as e:
            print(f"  ⚠️  Failed to parse Gemini response: {str(e)}")
            return []
    
    def _generate_chart(
        self,
        spec: Dict[str, Any],
        report_id: int,
        company_name: str,
        chart_num: int
    ) -> Optional[str]:
        """Generate a single chart from specification"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        from pathlib import Path
        
        chart_type = spec.get('chart_type', 'bar')
        title = spec.get('title', f'Chart {chart_num}')
        data = spec.get('data', {})
        x_label = spec.get('x_label', '')
        y_label = spec.get('y_label', '')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate chart based on type
        if chart_type == 'bar':
            self._create_bar_chart(ax, data, title, x_label, y_label)
        elif chart_type == 'horizontal_bar':
            self._create_horizontal_bar_chart(ax, data, title, x_label, y_label)
        elif chart_type == 'line':
            self._create_line_chart(ax, data, title, x_label, y_label)
        elif chart_type == 'pie':
            self._create_pie_chart(ax, data, title)
        elif chart_type == 'scatter':
            self._create_scatter_chart(ax, data, title, x_label, y_label)
        elif chart_type == 'stacked_bar':
            self._create_stacked_bar_chart(ax, data, title, x_label, y_label)
        else:
            self._create_bar_chart(ax, data, title, x_label, y_label)  # Default to bar
        
        # Save chart
        output_dir = Path("outputs/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_company = company_name.replace(' ', '_').replace('.', '')
        filename = f"report_{report_id}_{safe_company}_viz_{chart_num}.png"
        filepath = output_dir / filename
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    def _create_bar_chart(self, ax, data, title, x_label, y_label):
        """Create a bar chart"""
        import seaborn as sns
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        sns.barplot(x=labels, y=values, ax=ax, palette='viridis')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(values):
            ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=9)
    
    def _create_horizontal_bar_chart(self, ax, data, title, x_label, y_label):
        """Create a horizontal bar chart"""
        import seaborn as sns
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        sns.barplot(y=labels, x=values, ax=ax, palette='viridis', orient='h')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
    
    def _create_line_chart(self, ax, data, title, x_label, y_label):
        """Create a line chart"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        ax.plot(labels, values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(values):
            ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=9)
    
    def _create_pie_chart(self, ax, data, title):
        """Create a pie chart"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        colors = sns.color_palette('viridis', len(labels))
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    def _create_scatter_chart(self, ax, data, title, x_label, y_label):
        """Create a scatter chart"""
        x_values = data.get('x_values', [])
        y_values = data.get('y_values', [])
        
        ax.scatter(x_values, y_values, s=100, alpha=0.6, color='#2E86AB')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.grid(True, alpha=0.3)
    
    def _create_stacked_bar_chart(self, ax, data, title, x_label, y_label):
        """Create a stacked bar chart"""
        import numpy as np
        
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])  # List of {name, values}
        
        bottom = np.zeros(len(labels))
        colors = sns.color_palette('viridis', len(datasets))
        
        for i, dataset in enumerate(datasets):
            values = dataset.get('values', [])
            name = dataset.get('name', f'Dataset {i+1}')
            ax.bar(labels, values, bottom=bottom, label=name, color=colors[i])
            bottom += np.array(values)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.legend()
        ax.tick_params(axis='x', rotation=45)
    
    def _generate_fallback_chart_specs(
        self,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any],
        company_name: str
    ) -> List[Dict[str, Any]]:
        """Generate basic fallback chart specifications if Gemini fails"""
        
        specs = []
        
        # Handle list input
        if isinstance(financial_data, list):
            financial_data = financial_data[0] if financial_data else {}
        
        # Chart 1: Revenue Growth - check different possible structures
        sales_forecast_data = None
        if 'sales_forecast' in predictions:
            sales_forecast_data = predictions['sales_forecast']
            # Handle both list and dict formats
            if isinstance(sales_forecast_data, dict):
                forecast_list = sales_forecast_data.get('forecast', [])
            elif isinstance(sales_forecast_data, list):
                forecast_list = sales_forecast_data
            else:
                forecast_list = []
            
            if forecast_list:
                forecast_list = forecast_list[:5]  # First 5 years
                specs.append({
                    "chart_type": "bar",
                    "title": f"{company_name} - Revenue Forecast",
                    "data": {
                        "labels": [str(f.get('year', '')) for f in forecast_list],
                        "values": [f.get('predicted_revenue', f.get('projected_sales', 0)) for f in forecast_list]
                    },
                    "x_label": "Year",
                    "y_label": "Revenue ($)",
                    "insights": "Revenue growth projection based on ML models"
                })
        
        # Chart 2: Scenario Analysis
        scenarios_data = predictions.get('scenarios', predictions.get('scenario_analysis', {}))
        if scenarios_data:
            # Handle dict format (scenario_name: {data})
            if isinstance(scenarios_data, dict):
                if 'scenarios' in scenarios_data:  # Nested structure
                    scenario_list = scenarios_data['scenarios']
                else:  # Direct format
                    scenario_list = [
                        {"scenario": k.replace('_', ' ').title(), "growth_rate": v.get('growth_rate', 0)}
                        for k, v in scenarios_data.items()
                    ]
            elif isinstance(scenarios_data, list):
                scenario_list = scenarios_data
            else:
                scenario_list = []
            
            if scenario_list:
                specs.append({
                    "chart_type": "horizontal_bar",
                    "title": "Growth Scenarios",
                    "data": {
                        "labels": [s.get('scenario', '') for s in scenario_list],
                        "values": [s.get('growth_rate', 0) for s in scenario_list]
                    },
                    "x_label": "Growth Rate (%)",
                    "y_label": "Scenario",
                    "insights": "Best/Base/Worst case growth scenarios"
                })
        
        # Chart 3: Risk Assessment
        risk_data = predictions.get('risk_metrics', predictions.get('risk_assessment', {}))
        if risk_data:
            financial_health = risk_data.get('financial_health_score', 0)
            if financial_health > 0:
                specs.append({
                    "chart_type": "pie",
                    "title": "Financial Health Breakdown",
                    "data": {
                        "labels": ["Health Score", "Risk Factor"],
                        "values": [
                            financial_health,
                            100 - financial_health
                        ]
                    },
                    "insights": f"Overall financial health: {risk_data.get('risk_level', 'N/A')}"
                })
        
        return specs


# Singleton instance for easy import
gemini_client = GeminiClient()
