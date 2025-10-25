# 📧 Investment Email Pipeline

**Adapted from friend's 4-file email pipeline architecture for financial investment context**

## 🎯 Overview

This standalone CLI pipeline generates personalized investment analysis emails:
1. **Ingest** - Extract financial data from database → Evidence text files
2. **LLM Analysis** - Use Groq AI to extract opportunities/risks/catalysts
3. **Email** - Send professional HTML emails via SendGrid

## 📁 Architecture

```
backend/email_pipeline/
├── 1_ingest.py          # Database → evidence/*.txt
├── 2_llm.py             # Evidence → LLM → leads/*.json
├── 3_email_sendgrid.py  # SendGrid sender + HTML template
├── orchestrate.py       # Main coordinator script
├── contacts.csv         # Investor email list
└── README.md            # This file

Generated directories:
├── evidence/            # Per-company financial data (text)
└── leads/               # Per-company investment analysis (JSON)
```

## 🚀 Quick Start

### 1. Environment Variables

Set these before running:

```bash
# Required for LLM analysis
export GROQ_API_KEY=gsk_your_key_here

# Required for sending emails (not needed in preview mode)
export SENDGRID_API_KEY=SG.your_key_here
export SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

### 2. Configure Contacts

Edit `contacts.csv` with investor emails:

```csv
company,email,name
microsoft,investor@fund.com,John Smith
apple,analyst@firm.com,Jane Doe
,portfolio@investment.com,Portfolio Manager
```

**Fields:**
- `company` - Filter by company name (leave empty to receive all companies)
- `email` - Recipient email address
- `name` - Recipient name for personalization

### 3. Run Pipeline

**Preview mode** (no actual sending):
```bash
cd backend/email_pipeline
python orchestrate.py --preview
```

**Production mode** (sends emails):
```bash
python orchestrate.py
```

**Custom contacts file:**
```bash
python orchestrate.py --contacts investors.csv
```

## 📊 What Happens

```
┌─────────────────────────────────────────────┐
│ 1. INGEST                                   │
│    Database → evidence/microsoft_2024.txt   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│ 2. LLM ANALYSIS (Groq AI)                   │
│    evidence/*.txt → leads/microsoft.json    │
│    Extracts:                                │
│    - Investment opportunities               │
│    - Risk factors                           │
│    - Growth catalysts                       │
│    - Overall rating                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│ 3. EMAIL (SendGrid)                         │
│    leads/*.json → HTML email                │
│    Professional template with:              │
│    - Executive summary                      │
│    - Color-coded sections                   │
│    - Rating badges                          │
└─────────────────────────────────────────────┘
```

## 🎨 Email Template

Professional HTML design:
- **Header**: Gradient purple with company logo placeholder
- **Rating Badge**: Visual investment rating (Buy/Hold/Sell)
- **Opportunities**: Green cards with potential/timeframe
- **Risks**: Red cards with severity/mitigation
- **Catalysts**: Purple cards with impact levels
- **Evidence**: Expandable sections with source data

## 🔧 Customization

### Change LLM Model

Edit `2_llm.py`:
```python
self.groq_client.chat_completion(
    model="llama-3.1-70b-versatile",  # Change this
    temperature=0.2,                   # Or adjust temperature
    messages=[...]
)
```

### Modify Email Template

Edit `3_email_sendgrid.py` → `create_investment_email_html()` function.

### Filter Companies

Edit database query in `1_ingest.py` → `ingest_from_database()`:
```python
reports = db.query(Report).filter(
    Report.company_name.ilike('%tech%')  # Add filters
).all()
```

## 📝 File Formats

### Evidence Files (`evidence/microsoft_2024.txt`)
```
Company: Microsoft Corporation
Year: 2024
Industry: Technology

=== FINANCIAL DATA ===
Revenue: $211.9B
Net Income: $72.4B
...
```

### Leads Files (`leads/microsoft.json`)
```json
{
  "company": "Microsoft Corporation",
  "year": 2024,
  "rating": "Strong Buy",
  "summary": "...",
  "opportunities": [
    {
      "title": "Cloud dominance",
      "potential": "High",
      "timeframe": "12-18 months",
      "evidence": "..."
    }
  ],
  "risks": [...],
  "catalysts": [...]
}
```

## 🐛 Troubleshooting

### "GROQ_API_KEY not set"
```bash
export GROQ_API_KEY=gsk_your_key_here
```

### "No financial data found"
- Check database has Report + Analysis records
- Verify database connection in `backend/app/database.py`
- Ensure `extracted_data_path` field points to valid JSON files

### "No leads extracted"
- Check `evidence/*.txt` files were created
- Verify GROQ_API_KEY is valid
- Check Groq API quota/limits

### "Email sending failed"
- Verify SENDGRID_API_KEY and SENDGRID_FROM_EMAIL
- Check SendGrid sender verification
- Use `--preview` flag to test without sending

## 🔗 Integration with Main App

This pipeline is **standalone** and can run independently. To integrate with the web app:

1. **Option A**: Keep separate (current approach)
   - Run manually: `python orchestrate.py`
   - Schedule with cron/Task Scheduler

2. **Option B**: Trigger from API
   - Create endpoint: `/api/leads/send-emails`
   - Call `EmailPipeline().run_full_pipeline()` from route

3. **Option C**: Background job
   - Use Celery/RQ to queue email jobs
   - Dashboard triggers pipeline execution

## 📚 Dependencies

From `requirements.txt`:
- `groq` - LLM API client
- `sendgrid` - Email service
- `sqlalchemy` - Database ORM
- Standard library: `os`, `json`, `csv`, `pathlib`

## 🎓 Credits

Architecture based on friend's proven 4-file email pipeline:
- File-based workflow (evidence → leads → email)
- Robust JSON extraction with fallbacks
- Professional HTML email templates
- CLI execution model

**Adapted for financial investment context:**
- Database input instead of CSV/Excel/PDF
- Companies instead of departments
- Investment opportunities/risks/catalysts instead of department leads

## 📞 Support

For issues or questions:
1. Check `evidence/` and `leads/` directories for intermediate files
2. Run with `--preview` flag to test without sending
3. Check environment variables are set correctly
4. Verify database connectivity
