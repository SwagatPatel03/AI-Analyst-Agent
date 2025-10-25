"""
Department Lead Extraction from Excel Files
Extracts department-wise leads (growth, status, work progress) from uploaded Excel files
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from app.utils.groq_client import GroqClient


class DepartmentLeadExtractor:
    """Extract department-wise leads from Excel files using Groq LLM"""
    
    def __init__(self):
        self.groq_client = GroqClient()
    
    def extract_leads_from_excel(self, excel_path: str) -> Dict:
        """
        Extract department-wise leads from Excel file
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            Dictionary with department leads
        """
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        # Read all sheets from Excel
        print(f"📊 Reading Excel file: {excel_path}")
        excel_data = pd.read_excel(excel_path, sheet_name=None)  # Read all sheets
        
        # Convert to text for LLM analysis
        excel_text = self._excel_to_text(excel_data)
        
        # Extract leads using LLM
        print("🤖 Analyzing with Groq LLM...")
        leads = self._extract_leads_with_llm(excel_text)
        
        return leads
    
    def _excel_to_text(self, excel_data: Dict[str, pd.DataFrame]) -> str:
        """Convert Excel data to readable text format"""
        
        text_parts = []
        
        for sheet_name, df in excel_data.items():
            text_parts.append(f"\n{'='*60}")
            text_parts.append(f"SHEET: {sheet_name}")
            text_parts.append(f"{'='*60}\n")
            
            # Convert DataFrame to readable text
            # Look for department-related columns
            dept_columns = [col for col in df.columns if any(
                keyword in col.lower() 
                for keyword in ['department', 'dept', 'division', 'team', 'unit']
            )]
            
            if dept_columns:
                # Group by department if found
                for dept_col in dept_columns:
                    if dept_col in df.columns:
                        text_parts.append(f"\n--- Grouped by {dept_col} ---\n")
                        for dept_name, group in df.groupby(dept_col):
                            text_parts.append(f"\nDepartment: {dept_name}")
                            text_parts.append(group.to_string(index=False))
                            text_parts.append("\n")
            else:
                # No department column, just show all data
                text_parts.append(df.to_string(index=False))
        
        return "\n".join(text_parts)
    
    def _extract_leads_with_llm(self, excel_text: str) -> Dict:
        """Use Groq LLM to extract department-wise leads"""
        
        system_prompt = """You are a business analyst analyzing department data from an Excel file.

Your task is to extract department-wise leads focusing on:
1. Growth indicators (revenue growth, expansion, new projects)
2. Status updates (ongoing work, completed tasks, milestones)
3. Work progress (performance metrics, achievements, challenges)

For each department found in the data, extract:
- Department name
- Growth indicators (percentage, trends, opportunities)
- Status (current state: growing/stable/declining)
- Key work items (projects, tasks, achievements)
- Concerns or risks (if any)

Return your analysis as a JSON object with this structure:
{
  "departments": [
    {
      "name": "Department Name",
      "growth": "Description of growth indicators and percentage",
      "status": "growing/stable/declining",
      "work_items": [
        "Key project or task 1",
        "Key project or task 2"
      ],
      "concerns": "Any risks or challenges identified"
    }
  ],
  "summary": "Overall summary of all departments"
}

If no clear departments are found, analyze the data as a single "General" department.
Return ONLY the JSON object, no other text."""

        user_prompt = f"""Analyze this Excel data and extract department-wise leads:

{excel_text}

Remember to focus on growth indicators, status, and work progress for each department."""

        try:
            response = self.groq_client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            
            # Extract JSON from response
            leads = self._extract_json_from_response(response)
            return leads
            
        except Exception as e:
            print(f"❌ LLM extraction error: {e}")
            return {
                "departments": [],
                "summary": f"Error extracting leads: {str(e)}"
            }
    
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response with fallbacks"""
        
        import re
        
        # Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON block with markdown code fences
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Fallback: return error
        return {
            "departments": [],
            "summary": "Could not extract structured data from response",
            "raw_response": response
        }


# Test function
def test_extraction():
    """Test the extraction with a sample Excel file"""
    
    # This would be called with actual uploaded Excel file path
    extractor = DepartmentLeadExtractor()
    
    # Example usage:
    # leads = extractor.extract_leads_from_excel("path/to/uploaded/file.xlsx")
    # print(json.dumps(leads, indent=2))
    
    print("DepartmentLeadExtractor ready!")


if __name__ == "__main__":
    test_extraction()
