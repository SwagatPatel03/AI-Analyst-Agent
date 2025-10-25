"""
4. ORCHESTRATE - Main pipeline coordinator
Adapted from friend's orchestrate.py for financial context
"""

import os
import sys
import csv
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from email_pipeline.ingest import FinancialDataIngestor
from email_pipeline.llm import InvestmentLeadExtractor
from email_pipeline.email_sendgrid import EmailSender, create_investment_email_html


class EmailPipeline:
    """Orchestrates the complete email pipeline"""
    
    def __init__(self, preview_mode: bool = False):
        self.preview_mode = preview_mode
        self.ingestor = FinancialDataIngestor()
        self.extractor = InvestmentLeadExtractor()
        self.sender = EmailSender() if not preview_mode else None
    
    def run_full_pipeline(self, contacts_csv: str = "contacts.csv"):
        """
        Run complete pipeline:
        1. Ingest financial data from database
        2. Extract investment leads with LLM
        3. Send emails to investors
        """
        
        print("=" * 70)
        print("🚀 STARTING EMAIL PIPELINE")
        print("=" * 70)
        
        # Step 1: Ingest data
        print("\n📥 STEP 1: Ingesting financial data...")
        from backend.app.database import SessionLocal
        db = SessionLocal()
        
        try:
            evidence_files = self.ingestor.ingest_from_database(db)
            if not evidence_files:
                print("❌ No financial data found to process")
                return
            print(f"✅ Created {len(evidence_files)} evidence files")
        finally:
            db.close()
        
        # Step 2: Extract leads
        print("\n🤖 STEP 2: Extracting investment leads with LLM...")
        all_leads = self.extractor.extract_all_leads()
        if not all_leads:
            print("❌ No leads extracted")
            return
        print(f"✅ Extracted leads for {len(all_leads)} companies")
        
        # Step 3: Load contacts
        print("\n📧 STEP 3: Loading investor contacts...")
        contacts = self._load_contacts(contacts_csv)
        if not contacts:
            print("❌ No contacts found in", contacts_csv)
            return
        print(f"✅ Loaded {len(contacts)} investor contacts")
        
        # Step 4: Send emails
        print("\n📨 STEP 4: Sending investment analysis emails...")
        self._send_all_emails(all_leads, contacts)
        
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETE")
        print("=" * 70)
    
    def _load_contacts(self, csv_path: str) -> list:
        """
        Load investor contacts from CSV file
        Expected format: company,email,name
        """
        contacts_file = Path(csv_path)
        if not contacts_file.exists():
            print(f"⚠️  Creating sample {csv_path} file...")
            self._create_sample_contacts(csv_path)
        
        contacts = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append({
                    'company': row.get('company', '').strip(),
                    'email': row.get('email', '').strip(),
                    'name': row.get('name', 'Investor').strip()
                })
        
        return [c for c in contacts if c['email']]  # Filter out empty emails
    
    def _create_sample_contacts(self, csv_path: str):
        """Create sample contacts.csv file"""
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['company', 'email', 'name'])
            writer.writerow(['microsoft', 'investor@fund.com', 'John Smith'])
            writer.writerow(['apple', 'analyst@firm.com', 'Jane Doe'])
            writer.writerow(['', 'portfolio@investment.com', 'Portfolio Manager'])  # Send all companies
        
        print(f"✅ Created sample {csv_path}")
        print(f"   Edit this file to add your investor contacts")
    
    def _send_all_emails(self, all_leads: dict, contacts: list):
        """Send emails to all investors based on their company preferences"""
        
        sent_count = 0
        failed_count = 0
        
        for contact in contacts:
            company_filter = contact['company'].lower() if contact['company'] else None
            email = contact['email']
            name = contact['name']
            
            # Determine which companies to send
            if company_filter:
                # Send only specific company
                companies_to_send = {k: v for k, v in all_leads.items() if company_filter in k.lower()}
            else:
                # Send all companies (for portfolio managers)
                companies_to_send = all_leads
            
            if not companies_to_send:
                print(f"⚠️  No leads found for {contact['company']} (skipping {email})")
                continue
            
            # Send email for each company
            for company, leads in companies_to_send.items():
                subject = f"Investment Analysis: {leads.get('company', company)} - {leads.get('rating', 'N/A')}"
                
                # Generate HTML
                html_content = create_investment_email_html(
                    company=leads.get('company', company),
                    year=leads.get('year', 2024),
                    rating=leads.get('rating', 'N/A'),
                    summary=leads.get('summary', ''),
                    opportunities=leads.get('opportunities', []),
                    risks=leads.get('risks', []),
                    catalysts=leads.get('catalysts', [])
                )
                
                # Preview or send
                if self.preview_mode:
                    print(f"\n📧 PREVIEW: Would send to {email}")
                    print(f"   Subject: {subject}")
                    print(f"   Companies: {', '.join(companies_to_send.keys())}")
                    
                    # Save preview HTML
                    preview_path = Path("email_previews")
                    preview_path.mkdir(exist_ok=True)
                    preview_file = preview_path / f"{company}_{email.replace('@', '_at_')}.html"
                    with open(preview_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    print(f"   Preview saved: {preview_file}")
                    sent_count += 1
                else:
                    # Actually send
                    success = self.sender.send_email(
                        to_email=email,
                        subject=subject,
                        html_content=html_content
                    )
                    
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
        
        # Summary
        print(f"\n📊 Email Summary:")
        print(f"   ✅ Sent: {sent_count}")
        if failed_count > 0:
            print(f"   ❌ Failed: {failed_count}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run investment email pipeline')
    parser.add_argument('--preview', action='store_true', help='Preview mode (no actual sending)')
    parser.add_argument('--contacts', default='contacts.csv', help='Path to contacts CSV file')
    
    args = parser.parse_args()
    
    # Check environment variables
    if not os.getenv('GROQ_API_KEY'):
        print("❌ GROQ_API_KEY environment variable not set")
        return
    
    if not args.preview and not os.getenv('SENDGRID_API_KEY'):
        print("❌ SENDGRID_API_KEY environment variable not set")
        print("   Use --preview flag to test without sending")
        return
    
    # Run pipeline
    pipeline = EmailPipeline(preview_mode=args.preview)
    pipeline.run_full_pipeline(contacts_csv=args.contacts)


if __name__ == "__main__":
    main()
