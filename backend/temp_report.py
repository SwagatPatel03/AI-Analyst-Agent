"""
Report generation service
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from typing import Dict, Any
from datetime import datetime
import os


class ReportGenerator:
    """Service for generating comprehensive PDF reports"""
    
    async def generate(
        self,
        analysis,
        include_predictions: bool = True,
        include_visualizations: bool = True
    ) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            analysis: Analysis model instance
            include_predictions: Include ML predictions
            include_visualizations: Include charts
            
        Returns:
            Path to generated report
        """
        output_dir = "outputs/reports"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"financial_report_{analysis.id}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Add custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        company_name = "Company" if not analysis.report.company_name else analysis.report.company_name
        title = Paragraph(f"Financial Analysis Report<br/>{company_name}", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y")
        metadata = Paragraph(
            f"<b>Report Generated:</b> {report_date}<br/>"
            f"<b>Analysis ID:</b> {analysis.id}<br/>"
            f"<b>Report Year:</b> {analysis.report.report_year or 'N/A'}",
            styles['Normal']
        )
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        summary = self._generate_executive_summary(analysis.extracted_data)
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Financial Metrics
        if analysis.extracted_data and 'financial_metrics' in analysis.extracted_data:
            story.append(Paragraph("Financial Metrics", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            table = self._create_metrics_table(analysis.extracted_data['financial_metrics'])
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Key Performance Indicators
        if analysis.extracted_data and 'kpis' in analysis.extracted_data:
            story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            table = self._create_kpi_table(analysis.extracted_data['kpis'])
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Visualizations
        if include_visualizations and analysis.visualizations:
            story.append(PageBreak())
            story.append(Paragraph("Financial Visualizations", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for viz_path in analysis.visualizations:
                if os.path.exists(viz_path):
                    img = Image(viz_path, width=6*inch, height=3.5*inch)
                    story.append(img)
                    story.append(Spacer(1, 20))
        
        # Predictions
        if include_predictions and analysis.predictions:
            story.append(PageBreak())
            story.append(Paragraph("Financial Forecasts & Predictions", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            predictions_text = self._format_predictions(analysis.predictions)
            story.append(Paragraph(predictions_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        summary_parts = []
        
        if 'company_info' in data:
            company_name = data['company_info'].get('company_name', 'The company')
            summary_parts.append(f"{company_name} financial analysis reveals ")
        else:
            summary_parts.append("The financial analysis reveals ")
        
        if 'financial_metrics' in data:
            metrics = data['financial_metrics']
            revenue = metrics.get('total_revenue', 0)
            net_income = metrics.get('net_income', 0)
            
            summary_parts.append(f"total revenue of ${revenue}M and net income of ${net_income}M. ")
        
        if 'kpis' in data:
            kpis = data['kpis']
            growth = kpis.get('revenue_growth', 0)
            margin = kpis.get('net_profit_margin', 0)
            
            summary_parts.append(f"The company demonstrates a revenue growth rate of {growth}% ")
            summary_parts.append(f"with a net profit margin of {margin}%. ")
        
        summary_parts.append("This report provides detailed insights into the company's financial health, performance metrics, and future projections.")
        
        return "".join(summary_parts)
    
    def _create_metrics_table(self, metrics: Dict[str, Any]) -> Table:
        """Create financial metrics table"""
        data = [["Metric", "Value (in millions)"]]
        
        for key, value in metrics.items():
            metric_name = key.replace('_', ' ').title()
            value_str = f"${value}" if value is not None else "N/A"
            data.append([metric_name, value_str])
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _create_kpi_table(self, kpis: Dict[str, Any]) -> Table:
        """Create KPI table"""
        data = [["KPI", "Value"]]
        
        for key, value in kpis.items():
            kpi_name = key.replace('_', ' ').title()
            if value is not None:
                # Add % for percentage metrics
                if 'growth' in key or 'margin' in key or 'roa' in key or 'roe' in key:
                    value_str = f"{value}%"
                else:
                    value_str = str(value)
            else:
                value_str = "N/A"
            data.append([kpi_name, value_str])
        
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _format_predictions(self, predictions: Dict[str, Any]) -> str:
        """Format predictions text"""
        parts = []
        
        if 'revenue_forecast' in predictions and predictions['revenue_forecast']:
            parts.append("<b>Revenue Forecast:</b><br/>")
            for forecast in predictions['revenue_forecast']:
                parts.append(f"Year {forecast['year']}: ${forecast['revenue']}M<br/>")
            parts.append("<br/>")
        
        if 'growth_forecast' in predictions and predictions['growth_forecast']:
            growth = predictions['growth_forecast']
            parts.append(f"<b>Growth Outlook:</b> {growth.get('trend', 'N/A')}<br/>")
            parts.append(f"Projected Growth Rate: {growth.get('projected_growth', 'N/A')}%<br/><br/>")
        
        if 'profitability_trend' in predictions and predictions['profitability_trend']:
            prof = predictions['profitability_trend']
            parts.append(f"<b>Profitability Analysis:</b><br/>")
            parts.append(f"Current Margin: {prof.get('current_margin', 'N/A')}%<br/>")
            parts.append(f"Trend: {prof.get('trend', 'N/A')}<br/>")
            parts.append(f"Recommendation: {prof.get('recommendation', 'N/A')}<br/>")
        
        return "".join(parts)
