"""
1. INGEST - Read financial reports and normalize to text files
Adapted from friend's 1_ingest.py for financial context
"""

import os
import json
from pathlib import Path
from typing import Dict, List


class FinancialDataIngestor:
    """Ingests financial reports and creates per-company text evidence files"""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "evidence"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def ingest_from_database(self, db_connection) -> Dict[str, str]:
        """
        Read extracted financial data from database and create evidence files
        
        Returns:
            Dict mapping company names to evidence file paths
        """
        from backend.app.models.report import Report
        from backend.app.models.analysis import Analysis
        
        reports = db_connection.query(Report).all()
        evidence_files = {}
        
        for report in reports:
            company_name = self._normalize_name(report.company_name)
            
            # Load extracted data
            if not report.extracted_data_path or not os.path.exists(report.extracted_data_path):
                print(f"⚠️  Skipping {company_name}: No extracted data")
                continue
            
            with open(report.extracted_data_path, 'r') as f:
                extracted_data = json.load(f)
            
            # Get predictions (optional)
            analysis = db_connection.query(Analysis).filter(
                Analysis.report_id == report.id,
                Analysis.analysis_type == "prediction"
            ).first()
            predictions = analysis.ml_predictions if analysis else None
            
            # Create evidence text
            evidence_text = self._create_evidence_text(
                company_name,
                report.report_year,
                extracted_data,
                predictions
            )
            
            # Write to file
            output_path = self.output_dir / f"{company_name}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(evidence_text)
            
            evidence_files[company_name] = str(output_path)
            print(f"✅ Created evidence file: {output_path}")
        
        return evidence_files
    
    def _normalize_name(self, name: str) -> str:
        """Normalize company name for file naming"""
        return name.lower().replace(' ', '_').replace('.', '').replace(',', '')
    
    def _create_evidence_text(
        self,
        company: str,
        year: int,
        extracted_data: Dict,
        predictions: Dict = None
    ) -> str:
        """Convert JSON financial data to readable text for LLM"""
        
        lines = [
            f"=== FINANCIAL EVIDENCE FOR {company.upper()} ===",
            f"Report Year: {year or 'N/A'}",
            "",
            "--- FINANCIAL METRICS ---"
        ]
        
        # Extract financial data
        financial_data = extracted_data.get('financial_data', {})
        
        # Key metrics
        metrics = financial_data.get('key_metrics', {})
        if metrics:
            lines.append("\nKey Financial Metrics:")
            for key, value in metrics.items():
                lines.append(f"  • {key}: {value}")
        
        # Revenue data
        revenue = financial_data.get('revenue', {})
        if revenue:
            lines.append("\nRevenue:")
            for key, value in revenue.items():
                lines.append(f"  • {key}: {value}")
        
        # Profitability
        profitability = financial_data.get('profitability', {})
        if profitability:
            lines.append("\nProfitability:")
            for key, value in profitability.items():
                lines.append(f"  • {key}: {value}")
        
        # Assets
        assets = financial_data.get('assets', {})
        if assets:
            lines.append("\nAssets:")
            for key, value in assets.items():
                lines.append(f"  • {key}: {value}")
        
        # Liabilities
        liabilities = financial_data.get('liabilities', {})
        if liabilities:
            lines.append("\nLiabilities:")
            for key, value in liabilities.items():
                lines.append(f"  • {key}: {value}")
        
        # Cash flow
        cash_flow = financial_data.get('cash_flow', {})
        if cash_flow:
            lines.append("\nCash Flow:")
            for key, value in cash_flow.items():
                lines.append(f"  • {key}: {value}")
        
        # Predictions (if available)
        if predictions:
            lines.append("\n--- ML PREDICTIONS ---")
            for key, value in predictions.items():
                if isinstance(value, dict):
                    lines.append(f"\n{key}:")
                    for k, v in value.items():
                        lines.append(f"  • {k}: {v}")
                else:
                    lines.append(f"  • {key}: {value}")
        
        lines.append("\n=== END EVIDENCE ===")
        return "\n".join(lines)


if __name__ == "__main__":
    # Standalone usage
    from backend.app.database import SessionLocal
    
    db = SessionLocal()
    ingestor = FinancialDataIngestor()
    
    print("🔄 Starting ingestion...")
    evidence_files = ingestor.ingest_from_database(db)
    
    print(f"\n✅ Created {len(evidence_files)} evidence files")
    for company, path in evidence_files.items():
        print(f"   {company}: {path}")
    
    db.close()
