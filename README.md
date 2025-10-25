# Finalyst: AI Analyst Agent

Finalyst is a full-stack, AI-powered financial analyst platform that automates the extraction, analysis, and reporting of company financials from annual reports. It combines advanced document processing, machine learning, and natural language interfaces to deliver actionable insights for finance professionals, investors, and business leaders.

## Table of Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Backend](#backend)
- [Frontend](#frontend)
- [Machine Learning & AI](#machine-learning--ai)
- [Data Flow](#data-flow)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Development & Contribution](#development--contribution)
- [License](#license)

## Features
- **Document Upload & Parsing**: Upload annual reports (PDF/DOCX). Extracts tables, text, and financial statements using AI and OCR.
- **Financial Data Extraction**: Structured extraction of income statement, balance sheet, cash flow, segment, and geographic data.
- **Excel & JSON Export**: Generates Excel and JSON files for downstream analysis.
- **Data Visualization**: Interactive charts and graphs for key metrics, trends, and segment breakdowns.
- **AI Chatbot**: Conversational interface to query financials, ratios, and trends using natural language.
- **Agentic Analyst**: Automated deep-dive analysis, SWOT, and executive summaries using LLMs (Groq, Gemini).
- **ML Predictions**: Growth, sales, and risk forecasting using ensemble ML models and Monte Carlo simulation.
- **Comprehensive Report Generation**: Produces professional PDF/HTML/Markdown reports with executive summary, analysis, and recommendations.
- **Email Automation**: Sends reports and alerts via email (Mailgun/SMTP).
- **User Authentication**: Secure login, JWT-based auth, and user-specific report management.

## Architecture Overview
```
ai-analyst-agent/
├── backend/          # FastAPI backend (APIs, ML, extraction)
├── frontend/         # React TypeScript frontend (UI, chatbot)
├── outputs/          # Generated reports, JSON, Excel
├── uploads/          # Uploaded annual reports
├── ml_models/        # Trained ML models (not in git)
├── .gitignore
└── README.md
```

## Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Document Processing**: PyPDF2, pdfplumber, python-docx
- **Data Extraction**: Custom logic + LLMs (Groq, Gemini)
- **ML/AI**: Scikit-learn, ensemble models, Monte Carlo, OpenAI/Gemini APIs
- **Email**: SMTP/Mailgun integration
- **Auth**: JWT, OAuth2
- **Testing**: Pytest

### Key Backend Modules
- `app/main.py`: FastAPI entrypoint
- `app/routes/`: API endpoints (upload, report, auth, chatbot)
- `app/services/`: Extraction, ML, report generation, email
- `app/models/`: SQLAlchemy models (User, Report, Analysis)
- `app/utils/`: Helpers (Gemini client, PDF, Excel)
- `outputs/`: Generated files (PDF, HTML, JSON, Excel)

## Frontend
- **Framework**: React.js (TypeScript)
- **Build Tool**: Vite
- **UI**: Custom + Tailwind CSS
- **State Management**: Context API
- **Auth**: JWT, protected routes
- **Features**: File upload, report dashboard, chatbot, download, user profile

### Key Frontend Modules
- `src/components/`: UI components (Header, Footer, Dashboard, Chatbot)
- `src/pages/`: Main pages (Landing, Overview, Login, Register)
- `src/services/`: API calls (reportService, authService)
- `src/context/`: Auth and global state

## Machine Learning & AI
- **Extraction**: LLM-powered parsing of tables, text, and financials
- **ML Models**: RandomForest, GradientBoost, Linear Regression (ensemble)
- **Forecasting**: Growth, sales, and risk with confidence intervals
- **Scenario Analysis**: Best/base/worst case projections
- **Anomaly Detection**: Outlier and seasonality checks
- **Industry Benchmarks**: Fallback to industry data if only one year available
- **LLM Summaries**: Executive summary, SWOT, and recommendations via Gemini/Groq

## Data Flow
1. **User uploads annual report** (PDF/DOCX)
2. **Backend extracts data** (tables, text, financials)
3. **ML/AI modules analyze and predict** (growth, risk, scenarios)
4. **Reports generated** (PDF, HTML, Excel, JSON)
5. **User interacts via dashboard and chatbot**
6. **Reports/alerts sent via email**

## Setup & Installation

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure your environment variables
alembic upgrade head  # Run DB migrations
python -m uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
# Configure your environment variables
npm run dev
```

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL connection string
- `GROQ_API_KEY`: Groq AI API key
- `GEMINI_API_KEY`: Google Gemini API key
- `SECRET_KEY`: JWT secret key
- `MAILGUN_API_KEY`/`SMTP_*`: Email service config

### Frontend (.env)
- `VITE_API_URL`: Backend API URL

## Development & Contribution
- Use feature branches and pull requests
- Write clear commit messages
- Add/maintain docstrings and comments
- Run tests before pushing
- Sensitive files and outputs are gitignored

## License
MIT License
