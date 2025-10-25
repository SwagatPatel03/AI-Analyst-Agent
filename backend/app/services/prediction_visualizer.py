"""
Generate visualizations from ML prediction data
Creates PNG charts from prediction results for embedding in reports
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, Any, List


class PredictionVisualizer:
    """Generate visualization charts from ML prediction data"""
    
    def __init__(self, output_dir: str = "outputs/visualizations"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def generate_all_visualizations(
        self,
        predictions: Dict[str, Any],
        report_id: int,
        company_name: str = "Company"
    ) -> List[str]:
        """
        Generate all visualization charts from predictions
        
        Returns:
            List of file paths to generated charts
        """
        viz_paths = []
        
        # 1. Sales Forecast Chart
        if predictions.get('sales_forecast'):
            path = self._plot_sales_forecast(
                predictions['sales_forecast'],
                report_id,
                company_name
            )
            if path:
                viz_paths.append(path)
        
        # 2. Scenario Analysis Chart
        if predictions.get('scenario_analysis'):
            path = self._plot_scenarios(
                predictions['scenario_analysis'],
                report_id,
                company_name
            )
            if path:
                viz_paths.append(path)
        
        # 3. Risk Assessment Chart
        if predictions.get('risk_assessment'):
            path = self._plot_risk_metrics(
                predictions['risk_assessment'],
                report_id,
                company_name
            )
            if path:
                viz_paths.append(path)
        
        # 4. Performance Metrics Chart
        if predictions.get('performance_metrics'):
            path = self._plot_performance(
                predictions['performance_metrics'],
                report_id,
                company_name
            )
            if path:
                viz_paths.append(path)
        
        return viz_paths
    
    def _plot_sales_forecast(
        self,
        forecast_data: Dict[str, Any],
        report_id: int,
        company_name: str
    ) -> str:
        """Generate sales forecast chart"""
        try:
            forecast = forecast_data.get('forecast', [])
            if not forecast:
                return None
            
            years = [item.get('year', f"Year {i+1}") for i, item in enumerate(forecast)]
            sales = [item.get('projected_sales', 0) for item in forecast]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plot bars
            bars = ax.bar(years, sales, color='#667eea', alpha=0.7, edgecolor='#333')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height/1e9:.1f}B',
                       ha='center', va='bottom', fontsize=9)
            
            ax.set_title(f'{company_name} - Sales Forecast', fontsize=14, fontweight='bold')
            ax.set_xlabel('Year', fontsize=11)
            ax.set_ylabel('Projected Sales ($)', fontsize=11)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1e9:.0f}B'))
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, f"report_{report_id}_sales_forecast.png")
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"  ⚠️  Failed to generate sales forecast chart: {e}")
            return None
    
    def _plot_scenarios(
        self,
        scenario_data: Dict[str, Any],
        report_id: int,
        company_name: str
    ) -> str:
        """Generate scenario analysis chart"""
        try:
            scenarios = scenario_data.get('scenarios', [])
            if not scenarios:
                return None
            
            scenario_names = [s.get('scenario', 'Unknown') for s in scenarios]
            growth_rates = [s.get('growth_rate', 0) for s in scenarios]
            probabilities = [s.get('probability', 0) for s in scenarios]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Growth rates
            colors = ['#2ecc71', '#3498db', '#e74c3c'][:len(scenarios)]
            bars1 = ax1.barh(scenario_names, growth_rates, color=colors, alpha=0.7)
            
            for i, bar in enumerate(bars1):
                width = bar.get_width()
                ax1.text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:.2f}%',
                        ha='left', va='center', fontsize=10, fontweight='bold')
            
            ax1.set_title('Growth Rate Scenarios', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Growth Rate (%)', fontsize=10)
            ax1.grid(True, alpha=0.3, axis='x')
            
            # Probabilities
            ax2.pie(probabilities, labels=scenario_names, autopct='%1.0f%%',
                   colors=colors, startangle=90)
            ax2.set_title('Scenario Probabilities', fontsize=12, fontweight='bold')
            
            plt.suptitle(f'{company_name} - Scenario Analysis', fontsize=14, fontweight='bold', y=1.02)
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, f"report_{report_id}_scenarios.png")
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"  ⚠️  Failed to generate scenario chart: {e}")
            return None
    
    def _plot_risk_metrics(
        self,
        risk_data: Dict[str, Any],
        report_id: int,
        company_name: str
    ) -> str:
        """Generate risk assessment chart"""
        try:
            risk_score = risk_data.get('risk_score', 0)
            health_score = risk_data.get('financial_health_score', 0)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            metrics = ['Risk Score', 'Financial Health']
            values = [risk_score, health_score]
            colors = ['#e74c3c' if risk_score > 50 else '#f39c12' if risk_score > 30 else '#2ecc71',
                     '#2ecc71' if health_score > 70 else '#f39c12' if health_score > 50 else '#e74c3c']
            
            bars = ax.barh(metrics, values, color=colors, alpha=0.7, edgecolor='#333')
            
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                       f'{int(width)}/100',
                       ha='left', va='center', fontsize=11, fontweight='bold')
            
            ax.set_xlim(0, 110)
            ax.set_xlabel('Score (0-100)', fontsize=11)
            ax.set_title(f'{company_name} - Risk Assessment', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add risk level
            risk_level = risk_data.get('risk_level', 'Unknown')
            ax.text(0.98, 0.02, f'Risk Level: {risk_level}',
                   transform=ax.transAxes,
                   ha='right', va='bottom',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, f"report_{report_id}_risk.png")
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"  ⚠️  Failed to generate risk chart: {e}")
            return None
    
    def _plot_performance(
        self,
        performance_data: Dict[str, Any],
        report_id: int,
        company_name: str
    ) -> str:
        """Generate performance metrics chart"""
        try:
            metrics = []
            values = []
            
            # Collect available metrics
            metric_map = {
                'historical_cagr': 'Historical CAGR',
                'projected_cagr_3y': '3Y Projected CAGR',
                'roic': 'ROIC',
                'roa': 'ROA',
                'roe': 'ROE'
            }
            
            for key, label in metric_map.items():
                if key in performance_data and performance_data[key] is not None:
                    metrics.append(label)
                    values.append(performance_data[key])
            
            if not metrics:
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            colors = ['#3498db', '#2ecc71', '#9b59b6', '#e67e22', '#1abc9c'][:len(metrics)]
            bars = ax.bar(metrics, values, color=colors, alpha=0.7, edgecolor='#333')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}%',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_ylabel('Percentage (%)', fontsize=11)
            ax.set_title(f'{company_name} - Performance Metrics', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=15, ha='right')
            
            plt.tight_layout()
            
            filepath = os.path.join(self.output_dir, f"report_{report_id}_performance.png")
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            
            return filepath
            
        except Exception as e:
            print(f"  ⚠️  Failed to generate performance chart: {e}")
            return None
