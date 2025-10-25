"""
Email Pipeline Package
Adapted from friend's 4-file architecture for financial investment context
"""

from .ingest import FinancialDataIngestor
from .llm import InvestmentLeadExtractor
from .email_sendgrid import EmailSender, create_investment_email_html

__all__ = [
    'FinancialDataIngestor',
    'InvestmentLeadExtractor', 
    'EmailSender',
    'create_investment_email_html'
]
