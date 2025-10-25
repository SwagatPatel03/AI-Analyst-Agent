from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

class DataValidator:
    
    def validate_and_clean(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted financial data"""
        
        # Create a copy to avoid modifying original
        cleaned_data = financial_data.copy()
        
        # Validate revenue data
        if 'revenue' in cleaned_data:
            cleaned_data['revenue'] = self._validate_revenue(cleaned_data['revenue'])
        
        # Validate net income
        if 'net_income' in cleaned_data:
            cleaned_data['net_income'] = self._validate_net_income(cleaned_data['net_income'])
        
        # Fill missing values in key metrics
        if 'key_metrics' in cleaned_data:
            cleaned_data['key_metrics'] = self._fill_missing_metrics(cleaned_data['key_metrics'])
        
        # Validate segment revenue
        if 'segment_revenue' in cleaned_data:
            cleaned_data['segment_revenue'] = self._validate_segments(cleaned_data['segment_revenue'])
        
        return cleaned_data
    
    def _validate_revenue(self, revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate revenue numbers"""
        if not revenue_data:
            return {"current_year": None, "previous_year": None, "currency": "USD"}
        
        # Ensure positive values
        if revenue_data.get('current_year') and revenue_data['current_year'] < 0:
            revenue_data['current_year'] = abs(revenue_data['current_year'])
        
        if revenue_data.get('previous_year') and revenue_data['previous_year'] < 0:
            revenue_data['previous_year'] = abs(revenue_data['previous_year'])
        
        # Set default currency
        if not revenue_data.get('currency'):
            revenue_data['currency'] = 'USD'
        
        return revenue_data
    
    def _validate_net_income(self, net_income_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate net income (can be negative)"""
        if not net_income_data:
            return {"current_year": None, "previous_year": None}
        
        return net_income_data
    
    def _fill_missing_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate missing metrics if possible"""
        if not metrics:
            return {}
        
        # If debt_to_equity is missing but we have the data, calculate it
        # (This would need access to balance sheet data)
        
        return metrics
    
    def _validate_segments(self, segments: list) -> list:
        """Validate segment revenue data"""
        if not segments:
            return []
        
        validated = []
        for segment in segments:
            if segment.get('segment') and segment.get('revenue') is not None:
                validated.append(segment)
        
        return validated
    
    def to_dataframe(self, financial_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert financial data to pandas DataFrame for analysis"""
        
        # Flatten nested structure
        flat_data = {
            'company_name': financial_data.get('company_name'),
            'report_year': financial_data.get('report_year'),
            'revenue_current': financial_data.get('revenue', {}).get('current_year'),
            'revenue_previous': financial_data.get('revenue', {}).get('previous_year'),
            'currency': financial_data.get('revenue', {}).get('currency'),
            'net_income_current': financial_data.get('net_income', {}).get('current_year'),
            'net_income_previous': financial_data.get('net_income', {}).get('previous_year'),
            'total_assets': financial_data.get('total_assets'),
            'total_liabilities': financial_data.get('total_liabilities'),
            'shareholders_equity': financial_data.get('shareholders_equity'),
            'operating_cash_flow': financial_data.get('cash_flow', {}).get('operating'),
            'investing_cash_flow': financial_data.get('cash_flow', {}).get('investing'),
            'financing_cash_flow': financial_data.get('cash_flow', {}).get('financing'),
            'eps': financial_data.get('key_metrics', {}).get('eps'),
            'pe_ratio': financial_data.get('key_metrics', {}).get('pe_ratio'),
            'roe': financial_data.get('key_metrics', {}).get('roe'),
            'debt_to_equity': financial_data.get('key_metrics', {}).get('debt_to_equity')
        }
        
        # Create DataFrame with single row
        df = pd.DataFrame([flat_data])
        
        return df

data_validator = DataValidator()
