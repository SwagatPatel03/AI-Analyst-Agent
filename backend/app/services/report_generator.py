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
        """Generate a data-driven executive summary using all available fields from the extracted JSON."""
        company = data.get('metadata', {}).get('company_name', 'The company')
        year = data.get('metadata', {}).get('fiscal_year', 'N/A')
        revenue = data.get('financial_statements', {}).get('income_statement', {}).get('current_year', {}).get('revenue')
        net_income = data.get('financial_statements', {}).get('income_statement', {}).get('current_year', {}).get('net_income')
        revenue_growth = data.get('financial_ratios', {}).get('growth', {}).get('revenue_growth_yoy')
        net_income_growth = data.get('financial_ratios', {}).get('growth', {}).get('net_income_growth_yoy')
        gross_margin = data.get('financial_ratios', {}).get('gross_margin')
        operating_margin = data.get('financial_ratios', {}).get('operating_margin')
        net_profit_margin = data.get('financial_ratios', {}).get('net_profit_margin')
        roe = data.get('financial_ratios', {}).get('roe')
        current_ratio = data.get('financial_ratios', {}).get('current_ratio')
        debt_to_equity = data.get('financial_ratios', {}).get('debt_to_equity')
        dividend_per_share = data.get('shareholder_returns', {}).get('dividend_per_share')
        total_dividends_paid = data.get('shareholder_returns', {}).get('total_dividends_paid')
        segment_analysis = data.get('segment_analysis', [])
        geo_analysis = data.get('geographic_analysis', [])
        ceo_summary = data.get('ceo_statement_summary')
        esg = data.get('esg_data', {}).get('esg_initiatives')

        summary = f"<b>{company} - Executive Summary (FY {year})</b><br/>"
        if revenue and net_income:
            summary += f"Microsoft reported revenue of <b>${revenue:,}M</b> and net income of <b>${net_income:,}M</b> for the fiscal year. "
        if revenue_growth is not None:
            summary += f"Revenue grew by <b>{revenue_growth:.1%}</b> year-over-year. "
        if net_income_growth is not None:
            summary += f"Net income increased by <b>{net_income_growth:.1%}</b> year-over-year. "
        if gross_margin is not None:
            summary += f"Gross margin was <b>{gross_margin:.2f}%</b>. "
        if operating_margin is not None:
            summary += f"Operating margin reached <b>{operating_margin:.2f}%</b>. "
        if net_profit_margin is not None:
            summary += f"Net profit margin was <b>{net_profit_margin:.2f}%</b>. "
        if roe is not None:
            summary += f"Return on equity (ROE) was <b>{roe:.2f}%</b>. "
        if current_ratio is not None:
            summary += f"Current ratio stood at <b>{current_ratio:.2f}</b>. "
        if debt_to_equity is not None:
            summary += f"Debt-to-equity ratio was <b>{debt_to_equity:.2f}</b>. "
        if dividend_per_share is not None:
            summary += f"Dividend per share was <b>${dividend_per_share}</b>. "
        if total_dividends_paid is not None:
            summary += f"Total dividends paid: <b>${total_dividends_paid:,}M</b>. "

        # Segment highlights
        if segment_analysis:
            top_segment = max(segment_analysis, key=lambda s: s.get('revenue_current', 0))
            summary += f"The largest segment was <b>{top_segment.get('segment_name')}</b> with revenue of <b>${top_segment.get('revenue_current', 0):,}M</b>. "

        # Geographic highlights
        if geo_analysis:
            top_region = max(geo_analysis, key=lambda r: r.get('revenue_current', 0))
            summary += f"Top region: <b>{top_region.get('region_name')}</b> (${top_region.get('revenue_current', 0):,}M). "

        # CEO/ESG
        if ceo_summary:
            summary += f"<br/><i>CEO Statement:</i> {ceo_summary} "
        if esg:
            summary += f"<br/><i>ESG Initiatives:</i> {esg} "

        summary += "<br/>This report provides a data-driven analysis of the company's financial health, performance, and outlook."
        return summary
    
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
    
    # NEW: Gemini-powered report generation methods
    
    def generate_gemini_report(
        self,
        company_name: str,
        financial_data: Dict[str, Any],
        predictions: Dict[str, Any],
        visualizations: list = None,
        report_id: int = None,
        generate_pdf: bool = True
    ) -> Dict[str, str]:
        """
        Generate AI-powered comprehensive report using Gemini
        
        Args:
            company_name: Company name
            financial_data: Financial data
            predictions: ML predictions
            visualizations: List of visualization paths
            report_id: Report ID (auto-generated if None)
            generate_pdf: Whether to generate PDF (requires WeasyPrint)
        
        Returns dict with paths to markdown, html, pdf files
        """
        from app.utils.gemini_client import gemini_client
        import markdown as md
        
        print(f"📊 Generating report for {company_name}...")
        
        # Generate report content with Gemini AI
        print("  🤖 Generating AI content with Gemini...")
        report_content = gemini_client.generate_report(
            company_name,
            financial_data,
            predictions,
            visualizations or []
        )
        
        if not report_content:
            raise Exception("Empty report content from Gemini API")
        
        word_count = len(report_content.split())
        print(f"  ✅ Generated {word_count:,} words")
        
        # Create report ID
        if report_id is None:
            report_id = int(datetime.now().timestamp())
        
        # Save in multiple formats with timestamp to ensure uniqueness on regeneration
        safe_name = company_name.replace(" ", "_").replace("/", "-").replace("\\", "-")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Save Markdown
        print("  📝 Saving Markdown...")
        md_path = f"outputs/reports/markdown/report_{report_id}_{safe_name}_{timestamp}.md"
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        
        # Add metadata to markdown
        md_with_metadata = f"""---
title: Financial Analysis Report - {company_name}
report_id: {report_id}
generated_at: {datetime.now().isoformat()}
word_count: {word_count}
---

{report_content}
"""
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_with_metadata)
        
        # 2. Generate HTML (visualizations removed as per user request)
        print("  🌐 Generating HTML...")
        html_content = md.markdown(
            report_content, 
            extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
        )
        
        # Visualization section removed as per user request
        # visualization_html = self._generate_visualization_section(visualizations or [])
        
        html_template = (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            f"    <title>Financial Analysis Report - {company_name}</title>\n"
            "    <style>\n"
            "        * { margin: 0; padding: 0; box-sizing: border-box; }\n"
            "        body {\n"
            "            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;\n"
            "            line-height: 1.8;\n"
            "            color: #333;\n"
            "            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n"
            "            padding: 20px;\n"
            "        }\n"
            "        .container {\n"
            "            max-width: 1000px;\n"
            "            margin: 0 auto;\n"
            "            background-color: white;\n"
            "            padding: 50px;\n"
            "            border-radius: 12px;\n"
            "            box-shadow: 0 10px 40px rgba(0,0,0,0.2);\n"
            "        }\n"
            "        .header {\n"
            "            text-align: center;\n"
            "            border-bottom: 3px solid #667eea;\n"
            "            padding-bottom: 30px;\n"
            "            margin-bottom: 40px;\n"
            "        }\n"
            "        .header h1 {\n"
            "            color: #2c3e50;\n"
            "            font-size: 2.5em;\n"
            "            margin-bottom: 15px;\n"
            "        }\n"
            "        .header .company {\n"
            "            font-size: 1.5em;\n"
            "            color: #667eea;\n"
            "            font-weight: 600;\n"
            "        }\n"
            "        .header .meta {\n"
            "            color: #7f8c8d;\n"
            "            font-size: 0.95em;\n"
            "            margin-top: 10px;\n"
            "        }\n"
            "        h1 {\n"
            "            color: #2c3e50;\n"
            "            margin-top: 40px;\n"
            "            margin-bottom: 20px;\n"
            "            border-bottom: 2px solid #3498db;\n"
            "            padding-bottom: 10px;\n"
            "        }\n"
            "        h2 {\n"
            "            color: #34495e;\n"
            "            margin-top: 35px;\n"
            "            margin-bottom: 15px;\n"
            "            border-left: 5px solid #3498db;\n"
            "            padding-left: 15px;\n"
            "        }\n"
            "        h3 {\n"
            "            color: #555;\n"
            "            margin-top: 25px;\n"
            "            margin-bottom: 12px;\n"
            "        }\n"
            "        p {\n"
            "            margin-bottom: 15px;\n"
            "            text-align: justify;\n"
            "        }\n"
            "        ul, ol {\n"
            "            margin: 15px 0;\n"
            "            padding-left: 30px;\n"
            "        }\n"
            "        li {\n"
            "            margin-bottom: 8px;\n"
            "        }\n"
            "        table {\n"
            "            width: 100%;\n"
            "            border-collapse: collapse;\n"
            "            margin: 25px 0;\n"
            "            box-shadow: 0 2px 10px rgba(0,0,0,0.1);\n"
            "            border-radius: 8px;\n"
            "            overflow: hidden;\n"
            "        }\n"
            "        thead {\n"
            "            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);\n"
            "            color: white;\n"
            "        }\n"
            "        th {\n"
            "            padding: 15px;\n"
            "            text-align: left;\n"
            "            font-weight: 600;\n"
            "        }\n"
            "        td {\n"
            "            padding: 12px 15px;\n"
            "            border-bottom: 1px solid #ecf0f1;\n"
            "        }\n"
            "        tbody tr:nth-child(even) {\n"
            "            background-color: #f2f2f2;\n"
            "        }\n"
            "        tbody tr:hover {\n"
            "            background-color: #f8f9fa;\n"
            "        }\n"
            "        code {\n"
            "            background-color: #f4f4f4;\n"
            "            padding: 2px 6px;\n"
            "            border-radius: 3px;\n"
            "            font-family: 'Courier New', monospace;\n"
            "        }\n"
            "        strong {\n"
            "            color: #2c3e50;\n"
            "            font-weight: 600;\n"
            "        }\n"
            "        .footer {\n"
            "            margin-top: 60px;\n"
            "            padding-top: 30px;\n"
            "            border-top: 2px solid #ecf0f1;\n"
            "            text-align: center;\n"
            "            color: #7f8c8d;\n"
            "            font-size: 0.9em;\n"
            "        }\n"
            "        .disclaimer {\n"
            "            background-color: #fff3cd;\n"
            "            border: 1px solid #ffc107;\n"
            "            border-radius: 8px;\n"
            "            padding: 15px;\n"
            "            margin-top: 20px;\n"
            "        }\n"
            "        @media print {\n"
            "            body { background: white; padding: 0; }\n"
            "            .container { box-shadow: none; }\n"
            "        }\n"
            "        @media (max-width: 768px) {\n"
            "            .viz-grid { grid-template-columns: 1fr; }\n"
            "        }\n"
            "    </style>\n"
            "</head>\n"
            "<body>\n"
            "    <div class=\"container\">\n"
            "        <div class=\"header\">\n"
            "            <h1>📊 Financial Analysis Report</h1>\n"
            f"            <div class=\"company\">{company_name}</div>\n"
            "            <div class=\"meta\">\n"
            f"                <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>\n"
            f"                <p><strong>Report ID:</strong> {report_id}</p>\n"
            f"                <p><strong>Word Count:</strong> {word_count:,} words</p>\n"
            "            </div>\n"
            "        </div>\n"
            "        \n"
            "        <div class=\"content\">\n"
            f"            {html_content}\n"
            "        </div>\n"
            "        <div class=\"footer\">\n"
            "            <p><strong>Finalyst</strong> | Powered by Advanced ML & Gemini AI</p>\n"
            f"            <p>Version 1.0 | {datetime.now().year}</p>\n"
            "            <div class=\"disclaimer\">\n"
            "                <p><strong>⚠️ Disclaimer:</strong> This report was generated automatically using AI-powered analysis. \n"
            "                Consult professional financial advisors before making investment decisions.</p>\n"
            "            </div>\n"
            "        </div>\n"
            "    </div>\n"
            "</body>\n"
            "</html>"
        )
        
        html_path = f"outputs/reports/html/report_{report_id}_{safe_name}_{timestamp}.html"
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        result = {
            "markdown": md_path,
            "html": html_path,
            "report_id": report_id,
            "word_count": word_count
        }
        
        # 3. Generate PDF using xhtml2pdf (cross-platform)
        if generate_pdf:
            try:
                print("  📄 Generating PDF...")
                from xhtml2pdf import pisa
                
                pdf_path = f"outputs/reports/pdf/report_{report_id}_{safe_name}_{timestamp}.pdf"
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                
                # Convert HTML to PDF
                with open(pdf_path, "wb") as pdf_file:
                    # Create PDF from HTML string
                    pisa_status = pisa.CreatePDF(
                        html_template.encode('utf-8'),
                        dest=pdf_file,
                        encoding='utf-8'
                    )
                    
                    if pisa_status.err:
                        raise Exception(f"PDF generation had {pisa_status.err} error(s)")
                
                result["pdf"] = pdf_path
                print(f"  ✅ PDF generated successfully")
            
            except ImportError:
                print("  ⚠️  xhtml2pdf not installed - PDF generation skipped")
                print("     Install with: pip install xhtml2pdf")
            
            except Exception as e:
                print(f"  ⚠️  PDF generation failed: {e}")
                # Try fallback to WeasyPrint (for Linux/Mac)
                try:
                    from weasyprint import HTML as WeasyHTML
                    pdf_path = f"outputs/reports/pdf/report_{report_id}_{safe_name}_{timestamp}.pdf"
                    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                    WeasyHTML(string=html_template).write_pdf(pdf_path)
                    result["pdf"] = pdf_path
                    print(f"  ✅ PDF generated successfully (using WeasyPrint)")
                except:
                    pass  # Silent fail, PDF is optional
        
        print(f"✅ Report generation complete!")
        
        return result
    
    def _generate_visualization_section(self, visualizations: list) -> str:
        """
        Generate HTML section for visualizations with embedded images
        
        Args:
            visualizations: List of visualization file paths
            
        Returns:
            HTML string with embedded visualizations
        """
        if not visualizations or len(visualizations) == 0:
            return ""
        
        import base64
        from pathlib import Path
        
        viz_items = []
        
        for viz_path in visualizations:
            try:
                # Check if file exists
                if not os.path.exists(viz_path):
                    continue
                
                # Get filename for caption
                filename = Path(viz_path).stem
                caption = filename.replace('_', ' ').title()
                
                # Read and encode image as base64
                with open(viz_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    
                    # Detect image format
                    ext = Path(viz_path).suffix.lower()
                    mime_type = {
                        '.png': 'image/png',
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg',
                        '.gif': 'image/gif',
                        '.svg': 'image/svg+xml'
                    }.get(ext, 'image/png')
                    
                    # Create data URL
                    img_url = f"data:{mime_type};base64,{img_base64}"
                    
                    viz_items.append(
                        "                    <div class=\"viz-item\">\n"
                        f"                        <img src=\"{img_url}\" alt=\"{caption}\">\n"
                        f"                        <div class=\"viz-caption\">{caption}</div>\n"
                        "                    </div>\n"
                    )
            
            except Exception as e:
                print(f"  ⚠️  Failed to embed visualization {viz_path}: {e}")
                continue
        
        if not viz_items:
            return ""
        
        return (
            "        <div class=\"visualizations\">\n"
            "            <h2>📈 Data Visualizations</h2>\n"
            "            <div class=\"viz-grid\">\n"
            f"                {''.join(viz_items)}\n"
            "            </div>\n"
            "        </div>\n"
        )


# Create singleton instance
report_generator = ReportGenerator()
