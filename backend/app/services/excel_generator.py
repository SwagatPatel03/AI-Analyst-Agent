from typing import Dict, Any
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import os

class ExcelGenerator:
    
    def generate_excel(self, financial_data: Dict[str, Any], output_path: str) -> str:
        """Generate formatted Excel file from financial data"""
        
        # Create Excel writer
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            
            # Sheet 1: Overview
            self._create_overview_sheet(financial_data, writer)
            
            # Sheet 2: Income Statement
            self._create_income_statement_sheet(financial_data, writer)
            
            # Sheet 3: Balance Sheet
            self._create_balance_sheet(financial_data, writer)
            
            # Sheet 4: Cash Flow
            self._create_cash_flow_sheet(financial_data, writer)
            
            # Sheet 5: Segment Analysis
            self._create_segment_sheet(financial_data, writer)
            
            # Sheet 6: Geographic Analysis
            self._create_geographic_sheet(financial_data, writer)
        
        return output_path
    
    def _create_overview_sheet(self, data: Dict[str, Any], writer):
        """Create overview sheet"""
        overview_data = {
            'Metric': ['Company Name', 'Report Year', 'Currency', 'Total Assets', 
                      'Total Liabilities', 'Shareholders Equity', 'EPS', 'P/E Ratio', 
                      'ROE', 'Debt to Equity'],
            'Value': [
                data.get('company_name', 'N/A'),
                data.get('report_year', 'N/A'),
                data.get('revenue', {}).get('currency', 'USD'),
                data.get('total_assets', 'N/A'),
                data.get('total_liabilities', 'N/A'),
                data.get('shareholders_equity', 'N/A'),
                data.get('key_metrics', {}).get('eps', 'N/A'),
                data.get('key_metrics', {}).get('pe_ratio', 'N/A'),
                data.get('key_metrics', {}).get('roe', 'N/A'),
                data.get('key_metrics', {}).get('debt_to_equity', 'N/A')
            ]
        }
        
        df = pd.DataFrame(overview_data)
        df.to_excel(writer, sheet_name='Overview', index=False)
    
    def _create_income_statement_sheet(self, data: Dict[str, Any], writer):
        """Create income statement sheet"""
        revenue = data.get('revenue', {})
        net_income = data.get('net_income', {})
        
        income_data = {
            'Item': ['Revenue', 'Net Income'],
            'Current Year': [
                revenue.get('current_year', 'N/A'),
                net_income.get('current_year', 'N/A')
            ],
            'Previous Year': [
                revenue.get('previous_year', 'N/A'),
                net_income.get('previous_year', 'N/A')
            ]
        }
        
        df = pd.DataFrame(income_data)
        
        # Calculate YoY growth
        if (revenue.get('current_year') and revenue.get('previous_year') and 
            revenue['previous_year'] != 0):
            revenue_growth = ((revenue['current_year'] - revenue['previous_year']) / 
                            revenue['previous_year']) * 100
            df.loc[len(df)] = ['Revenue Growth %', revenue_growth, 'N/A']
        
        df.to_excel(writer, sheet_name='Income Statement', index=False)
    
    def _create_balance_sheet(self, data: Dict[str, Any], writer):
        """Create balance sheet"""
        balance_data = {
            'Item': ['Total Assets', 'Total Liabilities', 'Shareholders Equity'],
            'Amount': [
                data.get('total_assets', 'N/A'),
                data.get('total_liabilities', 'N/A'),
                data.get('shareholders_equity', 'N/A')
            ]
        }
        
        df = pd.DataFrame(balance_data)
        df.to_excel(writer, sheet_name='Balance Sheet', index=False)
    
    def _create_cash_flow_sheet(self, data: Dict[str, Any], writer):
        """Create cash flow sheet"""
        cash_flow = data.get('cash_flow', {})
        
        cf_data = {
            'Type': ['Operating Activities', 'Investing Activities', 'Financing Activities'],
            'Amount': [
                cash_flow.get('operating', 'N/A'),
                cash_flow.get('investing', 'N/A'),
                cash_flow.get('financing', 'N/A')
            ]
        }
        
        df = pd.DataFrame(cf_data)
        df.to_excel(writer, sheet_name='Cash Flow', index=False)
    
    def _create_segment_sheet(self, data: Dict[str, Any], writer):
        """Create segment analysis sheet"""
        segments = data.get('segment_revenue', [])
        
        if segments:
            df = pd.DataFrame(segments)
            df.to_excel(writer, sheet_name='Segment Analysis', index=False)
        else:
            # Create empty sheet with headers
            df = pd.DataFrame(columns=['segment', 'revenue'])
            df.to_excel(writer, sheet_name='Segment Analysis', index=False)
    
    def _create_geographic_sheet(self, data: Dict[str, Any], writer):
        """Create geographic analysis sheet"""
        geographic = data.get('geographic_revenue', [])
        
        if geographic:
            df = pd.DataFrame(geographic)
            df.to_excel(writer, sheet_name='Geographic Analysis', index=False)
        else:
            df = pd.DataFrame(columns=['region', 'revenue'])
            df.to_excel(writer, sheet_name='Geographic Analysis', index=False)

excel_generator = ExcelGenerator()