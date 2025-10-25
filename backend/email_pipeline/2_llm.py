"""
2. LLM - Use AI to extract investment leads from financial evidence
Adapted from friend's 2_llm.py for financial context
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List
from groq import Groq


class InvestmentLeadExtractor:
    """Uses LLM to extract investment opportunities from financial evidence"""
    
    def __init__(self, evidence_dir: str = "evidence", output_dir: str = "leads"):
        self.evidence_dir = Path(evidence_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Groq client
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)
    
    def extract_all_leads(self) -> Dict[str, Dict]:
        """Extract investment leads for all companies with evidence files"""
        
        leads = {}
        evidence_files = list(self.evidence_dir.glob("*.txt"))
        
        print(f"🔍 Found {len(evidence_files)} evidence files")
        
        for evidence_file in evidence_files:
            company = evidence_file.stem
            print(f"\n📊 Analyzing {company}...")
            
            # Read evidence
            with open(evidence_file, 'r', encoding='utf-8') as f:
                evidence = f.read()
            
            # Extract leads with LLM
            try:
                company_leads = self._extract_leads_with_llm(company, evidence)
                leads[company] = company_leads
                
                # Save to individual JSON file
                output_path = self.output_dir / f"{company}_leads.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(company_leads, f, indent=2)
                
                print(f"✅ Extracted {len(company_leads.get('opportunities', []))} opportunities")
                print(f"   Saved to: {output_path}")
                
            except Exception as e:
                print(f"❌ Failed to extract leads for {company}: {e}")
                continue
        
        return leads
    
    def _extract_leads_with_llm(self, company: str, evidence: str) -> Dict:
        """
        Call Groq LLM to analyze financial evidence and extract structured leads
        Matches friend's approach but with investment context
        """
        
        system_prompt = """You are a financial analyst assistant. Analyze company financial data and extract:

1. **Investment Opportunities**: Specific actionable investment opportunities
2. **Risk Factors**: Financial or operational risks to consider
3. **Growth Catalysts**: Events or trends that could drive growth
4. **Investment Rating**: Overall recommendation (Strong Buy, Buy, Hold, Sell, Strong Sell)

For each opportunity/risk/catalyst:
- title: Short descriptive title
- evidence: Specific data points from financial evidence
- potential/severity/impact: High, Medium, or Low
- timeframe/mitigation: Additional context

Return ONLY valid JSON in this format:
{
  "company": "Company Name",
  "rating": "Buy/Hold/Sell",
  "summary": "Brief 1-2 sentence summary",
  "opportunities": [
    {"title": "...", "evidence": "...", "potential": "High/Medium/Low", "timeframe": "Short/Medium/Long-term"}
  ],
  "risks": [
    {"title": "...", "evidence": "...", "severity": "High/Medium/Low", "mitigation": "..."}
  ],
  "catalysts": [
    {"title": "...", "evidence": "...", "impact": "High/Medium/Low"}
  ]
}"""

        user_prompt = f"""Company: {company}

Financial Evidence:
---
{evidence}
---

Analyze this financial data and return JSON with investment opportunities, risks, and catalysts."""

        # Call Groq API
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON (robust extraction from friend's code)
        json_text = self._extract_first_json_block(content)
        leads_data = json.loads(json_text)
        
        return leads_data
    
    def _extract_first_json_block(self, text: str) -> str:
        """
        Robustly extract JSON from LLM response
        COPIED FROM FRIEND'S CODE - Works perfectly!
        """
        # Try bracket slice first
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1 and s < e:
            candidate = text[s:e+1]
            try:
                json.loads(candidate)
                return candidate
            except:
                pass
        
        # Try regex patterns
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # nested
            r'\{.*?\}',  # simple
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except:
                    continue
        
        # Fallback: return whatever is between first { and last }
        if s != -1 and e != -1:
            return text[s:e+1]
        
        raise ValueError("No valid JSON found in response")


if __name__ == "__main__":
    print("🤖 Starting LLM lead extraction...")
    
    extractor = InvestmentLeadExtractor()
    all_leads = extractor.extract_all_leads()
    
    print(f"\n✅ Extraction complete! Processed {len(all_leads)} companies")
    
    # Summary
    total_opportunities = sum(len(leads.get('opportunities', [])) for leads in all_leads.values())
    total_risks = sum(len(leads.get('risks', [])) for leads in all_leads.values())
    total_catalysts = sum(len(leads.get('catalysts', [])) for leads in all_leads.values())
    
    print(f"\n📊 Summary:")
    print(f"   Total Opportunities: {total_opportunities}")
    print(f"   Total Risks: {total_risks}")
    print(f"   Total Catalysts: {total_catalysts}")
