import pdfplumber
import PyPDF2
from typing import Dict, List, Any
import re

class PDFProcessor:
    
    @staticmethod
    def extract_text_pdfplumber(file_path: str) -> str:
        """Extract text from PDF using pdfplumber (better for tables)"""
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return "\n\n".join(text_content)
    
    @staticmethod
    def extract_tables(file_path: str) -> List[List[List[str]]]:
        """Extract tables from PDF"""
        all_tables = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
        
        return all_tables
    
    @staticmethod
    def get_metadata(file_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
            
            return {
                "pages": len(pdf_reader.pages),
                "title": metadata.get('/Title', 'Unknown'),
                "author": metadata.get('/Author', 'Unknown'),
                "subject": metadata.get('/Subject', 'Unknown'),
                "creator": metadata.get('/Creator', 'Unknown')
            }
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep financial symbols
        text = re.sub(r'[^\w\s\.,\-\$\%\(\)]', '', text)
        return text.strip()

pdf_processor = PDFProcessor()
