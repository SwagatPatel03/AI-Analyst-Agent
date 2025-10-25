"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.routes import auth, upload, analysis, chatbot, report, leads, department_leads

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered financial analyst agent",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="outputs"), name="static")

# Register all routes
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(chatbot.router)
app.include_router(report.router)
app.include_router(leads.router)  # Investment lead generation routes
app.include_router(department_leads.router)  # Department lead extraction from Excel

@app.get("/")
async def root():
    return {
        "message": "AI Analyst Agent API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "auth": "/auth",
            "upload": "/upload",
            "analysis": "/analysis",
            "chatbot": "/chatbot",
            "report": "/report",
            "leads": "/leads"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
