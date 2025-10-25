"""
Chatbot service for financial queries
AI-powered conversational interface for financial data analysis
"""
from typing import List, Dict, Any, Optional
import json
from app.utils.groq_client import groq_client


class ChatbotService:
    """Service for handling financial chatbot queries with conversation history"""
    
    def __init__(self):
        self.max_history = 10  # Keep last 10 messages for context
    
    def chat(
        self, 
        user_message: str, 
        financial_data: Dict[str, Any],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with financial data context
        
        Args:
            user_message: User's question
            financial_data: Financial data from report
            chat_history: Previous conversation history
        
        Returns:
            Response with answer and updated history
        """
        
        if chat_history is None:
            chat_history = []
        
        # Prepare context from financial data
        context = self._prepare_context(financial_data)
        
        # Build messages for AI
        messages = self._build_messages(context, user_message, chat_history)
        
        # Get response from Groq AI
        response = groq_client.chat_completion(messages)
        
        # Update chat history
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": response})
        
        # Trim history if too long
        if len(chat_history) > self.max_history * 2:
            chat_history = chat_history[-self.max_history * 2:]
        
        return {
            "answer": response,
            "chat_history": chat_history
        }
    
    def _prepare_context(self, financial_data: Dict[str, Any]) -> str:
        """Prepare financial data as context string"""
        
        # DEBUG: Print what we received
        print("\n" + "="*60)
        print("🔍 DEBUG: Checking financial_data structure")
        print(f"Keys in financial_data: {list(financial_data.keys())}")
        print("="*60 + "\n")
        
        # Handle nested JSON structure from Gemini extraction
        metadata = financial_data.get('metadata', {})
        financial_statements = financial_data.get('financial_statements', {})
        financial_ratios = financial_data.get('financial_ratios', {})
        segment_analysis = financial_data.get('segment_analysis', [])
        geographic_analysis = financial_data.get('geographic_analysis', [])
        
        # Extract company info
        company_name = metadata.get('company_name', 'Unknown')
        fiscal_year = metadata.get('fiscal_year', 'Unknown')
        currency = metadata.get('currency', 'USD')
        
        # Extract income statement data
        income_stmt = financial_statements.get('income_statement', {})
        current_income = income_stmt.get('current_year', {})
        previous_income = income_stmt.get('previous_year', {})
        
        # Extract balance sheet data
        balance_sheet = financial_statements.get('balance_sheet', {})
        current_balance = balance_sheet.get('current_year', {})
        previous_balance = balance_sheet.get('previous_year', {})
        
        # Extract cash flow data
        cash_flow = financial_statements.get('cash_flow', {})
        current_cf = cash_flow.get('current_year', {})
        previous_cf = cash_flow.get('previous_year', {})
        
        # Build comprehensive context
        context = f"""
Financial Data for {company_name} (Fiscal Year: {fiscal_year}):

REVENUE & INCOME:
- Current Year Revenue: {self._format_number(current_income.get('revenue'))} {currency}
- Previous Year Revenue: {self._format_number(previous_income.get('revenue'))} {currency}
- Current Year Net Income: {self._format_number(current_income.get('net_income'))} {currency}
- Previous Year Net Income: {self._format_number(previous_income.get('net_income'))} {currency}
- Current Year Gross Profit: {self._format_number(current_income.get('gross_profit'))} {currency}
- Current Year Operating Income: {self._format_number(current_income.get('operating_income'))} {currency}

BALANCE SHEET:
- Total Assets (Current): {self._format_number(current_balance.get('total_assets'))} {currency}
- Total Assets (Previous): {self._format_number(previous_balance.get('total_assets'))} {currency}
- Total Liabilities (Current): {self._format_number(current_balance.get('total_liabilities'))} {currency}
- Total Equity (Current): {self._format_number(current_balance.get('total_equity'))} {currency}
- Cash and Equivalents: {self._format_number(current_balance.get('cash_and_equivalents'))} {currency}

CASH FLOW:
- Operating Cash Flow: {self._format_number(current_cf.get('operating_activities'))} {currency}
- Investing Cash Flow: {self._format_number(current_cf.get('investing_activities'))} {currency}
- Financing Cash Flow: {self._format_number(current_cf.get('financing_activities'))} {currency}

FINANCIAL RATIOS:
- EPS (Current): {self._format_number(financial_ratios.get('current_year', {}).get('earnings_per_share'))}
- EPS (Previous): {self._format_number(financial_ratios.get('previous_year', {}).get('earnings_per_share'))}
- P/E Ratio: {self._format_number(financial_ratios.get('current_year', {}).get('price_to_earnings_ratio'))}
- ROE: {self._format_number(financial_ratios.get('current_year', {}).get('return_on_equity'))}%
- ROA: {self._format_number(financial_ratios.get('current_year', {}).get('return_on_assets'))}%
- Debt-to-Equity: {self._format_number(financial_ratios.get('current_year', {}).get('debt_to_equity_ratio'))}
- Current Ratio: {self._format_number(financial_ratios.get('current_year', {}).get('current_ratio'))}
- Gross Margin: {self._format_number(financial_ratios.get('current_year', {}).get('gross_margin'))}%
- Operating Margin: {self._format_number(financial_ratios.get('current_year', {}).get('operating_margin'))}%
"""
        
        # Add segment analysis if available
        if segment_analysis and len(segment_analysis) > 0:
            context += "\nSEGMENT REVENUE:\n"
            for segment in segment_analysis:
                seg_name = segment.get('segment_name', 'Unknown')
                current_rev = self._format_number(segment.get('revenue_current'))
                previous_rev = self._format_number(segment.get('revenue_previous'))
                context += f"- {seg_name}: Current {current_rev} {currency}, Previous {previous_rev} {currency}\n"
        
        # Add geographic analysis if available
        if geographic_analysis and len(geographic_analysis) > 0:
            context += "\nGEOGRAPHIC REVENUE:\n"
            for region in geographic_analysis:
                region_name = region.get('region_name', 'Unknown')
                current_rev = self._format_number(region.get('revenue_current'))
                previous_rev = self._format_number(region.get('revenue_previous'))
                context += f"- {region_name}: Current {current_rev} {currency}, Previous {previous_rev} {currency}\n"
        
        return context
    
    def _format_number(self, value: Any) -> str:
        """Format number for display, handle None/null values"""
        if value is None or value == "":
            return "N/A"
        if isinstance(value, (int, float)):
            # Format with commas for readability
            return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
        return str(value)
    
    def _build_messages(
        self, 
        context: str, 
        user_message: str, 
        chat_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Build message array for AI"""
        
        system_message = {
            "role": "system",
            "content": f"""You are a helpful financial analyst AI assistant. 
You have access to financial data for a company and can answer questions about it.

{context}

Instructions:
- Answer questions based on the financial data provided
- Be precise with numbers and cite specific metrics
- If data is not available, clearly state that
- Provide insights and analysis when appropriate
- Calculate growth rates, ratios, and trends when relevant
- Keep responses concise but informative"""
        }
        
        messages = [system_message]
        
        # Add chat history
        messages.extend(chat_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages


# Global instance
chatbot_service = ChatbotService()
