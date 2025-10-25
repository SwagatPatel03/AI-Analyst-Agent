from typing import Dict, Any
import json
import os
from app.services.pdf_processor import pdf_processor
from app.utils.gemini_client import GeminiClient

class DataExtractor:
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def extract_from_pdf(self, file_path: str, company_name: str) -> Dict[str, Any]:
        """Main extraction pipeline"""
        
        # Step 1: Extract text from PDF
        print(f"\n{'='*60}")
        print(f"📄 Starting PDF extraction for: {company_name}")
        print(f"{'='*60}")
        print("Step 1/5: Extracting text from PDF...")
        raw_text = pdf_processor.extract_text_pdfplumber(file_path)
        print(f"✅ Extracted {len(raw_text)} characters")
        
        # Step 2: Clean text
        print("\nStep 2/5: Cleaning text...")
        cleaned_text = pdf_processor.clean_text(raw_text)
        print(f"✅ Cleaned text: {len(cleaned_text)} characters")
        
        # Step 3: Extract tables
        print("\nStep 3/5: Extracting tables...")
        tables = pdf_processor.extract_tables(file_path)
        print(f"✅ Found {len(tables)} tables")
        
        # Step 4: Use Gemini AI to extract structured financial data
        print("\nStep 4/6: Using Gemini AI to extract financial data (this may take 1-2 minutes)...")
        financial_data = self.gemini_client.extract_financial_data(cleaned_text, company_name)
        print("✅ Financial data extracted successfully")
        
        # Step 5: Extract ML-ready data for predictions
        print("\nStep 5/6: Extracting ML-ready data for predictions...")
        ml_ready_data = self.gemini_client.extract_ml_ready_data(cleaned_text, company_name)
        print("✅ ML-ready data extracted successfully")
        
        # Step 6: Add metadata
        print("\nStep 6/6: Adding metadata...")
        metadata = pdf_processor.get_metadata(file_path)
        print("✅ Metadata added")
        
        # Combine all extracted data
        complete_data = {
            "metadata": metadata,
            "financial_data": financial_data,
            "ml_ready_data": ml_ready_data,  # NEW: ML-ready data for predictions
            "tables_count": len(tables),
            "extraction_success": True
        }
        
        print(f"\n{'='*60}")
        print(f"✅ PDF extraction completed successfully!")
        print(f"{'='*60}\n")
        
        return complete_data
    
    def save_extracted_data(self, data: Dict[str, Any], output_path: str) -> str:
        """Save extracted data as JSON"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def save_ml_ready_data(self, ml_data: Dict[str, Any], output_path: str) -> str:
        """
        Save ML-ready data as a separate JSON file for ML predictor.
        This file is optimized for machine learning predictions.
        """
        # Create ml_data directory if it doesn't exist
        ml_dir = os.path.join(os.path.dirname(output_path), '..', 'ml_data')
        os.makedirs(ml_dir, exist_ok=True)
        
        # Create filename: company_name_ml.json
        filename = os.path.basename(output_path).replace('.json', '_ml.json')
        ml_path = os.path.join(ml_dir, filename)
        
        with open(ml_path, 'w') as f:
            json.dump(ml_data, f, indent=2)
        
        print(f"💾 ML-ready data saved to: {ml_path}")
        return ml_path

data_extractor = DataExtractor()
