"""
Chatbot routes - API endpoints for both chatbot services
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os

from app.database import get_db
from app.models.report import Report
from app.models.analysis import Analysis
from app.routes.auth import oauth2_scheme
from app.services import auth_service
from app.services.chatbot_service import chatbot_service
from app.services.agentic_analyst import agentic_analyst

# Note: Prefix added for frontend compatibility
router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# ==================== Pydantic Schemas ====================

class ChatMessage(BaseModel):
    """Simple chat message schema"""
    message: str


class AgenticQuery(BaseModel):
    """Agentic analyst query schema"""
    query: str


class ChatRequest(BaseModel):
    """Chat request schema (legacy support)"""
    message: str
    analysis_id: int
    chat_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    answer: str
    chat_history: Optional[List[Dict[str, str]]] = None
    context: Optional[dict] = None
    report_id: Optional[int] = None


class AgenticRequest(BaseModel):
    """Agentic analyst request schema (legacy support)"""
    query: str
    report_id: int


class AgenticResponse(BaseModel):
    """Agentic analyst response schema"""
    success: bool
    query: str
    code: Optional[str] = None
    result: Optional[Any] = None
    explanation: str
    error: Optional[str] = None
    attempts: Optional[int] = None


# ==================== Financial Chatbot Endpoints ====================

@router.post("/chat/{report_id}", response_model=ChatResponse)
async def chat_with_report(
    report_id: int,
    chat_message: ChatMessage,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Chat about financial report data with conversation history
    
    This endpoint provides conversational AI for financial Q&A.
    Chat history is automatically managed and persisted in the database.
    
    Args:
        report_id: ID of the report to chat about
        chat_message: Message from the user
        token: Authentication token
        db: Database session
        
    Returns:
        ChatResponse with answer and report_id
    """
    # Authenticate
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Load financial data
    if not os.path.exists(report.extracted_data_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial data not found"
        )
    
    with open(report.extracted_data_path, 'r') as f:
        data = json.load(f)
    
    # Pass the entire data object (it already has metadata, financial_statements, etc.)
    financial_data = data
    
    # Get or create analysis record for chat history
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "chat"
    ).first()
    
    chat_history = []
    if analysis and analysis.chat_history:
        chat_history = analysis.chat_history
    
    try:
        # Get chatbot response
        response = chatbot_service.chat(
            chat_message.message,
            financial_data,
            chat_history
        )
        
        # Update chat history in database
        if analysis:
            analysis.chat_history = response['chat_history']
        else:
            analysis = Analysis(
                report_id=report_id,
                user_id=user.id,
                analysis_type="chat",
                chat_history=response['chat_history']
            )
            db.add(analysis)
        
        db.commit()
        
        return ChatResponse(
            answer=response['answer'],
            report_id=report_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/chat/history/{report_id}")
async def get_chat_history(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get chat history for a report
    
    Returns all previous chat messages for the given report.
    
    Args:
        report_id: ID of the report
        token: Authentication token
        db: Database session
        
    Returns:
        Dictionary with chat_history list
    """
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "chat"
    ).first()
    
    if not analysis:
        return {"chat_history": []}
    
    return {"chat_history": analysis.chat_history or []}


@router.delete("/chat/history/{report_id}")
async def clear_chat_history(
    report_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Clear chat history for a report
    
    Deletes all chat messages for the given report.
    
    Args:
        report_id: ID of the report
        token: Authentication token
        db: Database session
        
    Returns:
        Success message
    """
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    analysis = db.query(Analysis).filter(
        Analysis.report_id == report_id,
        Analysis.user_id == user.id,
        Analysis.analysis_type == "chat"
    ).first()
    
    if analysis:
        analysis.chat_history = []
        db.commit()
    
    return {"message": "Chat history cleared"}


# ==================== Agentic Analyst Endpoints ====================

@router.post("/agent/analyze/{report_id}", response_model=AgenticResponse)
async def agentic_analysis(
    report_id: int,
    query: AgenticQuery,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Perform agentic analysis with code execution
    
    This endpoint uses AI to generate and execute Python code
    for deep financial analysis. The AI agent:
    1. Analyzes your query
    2. Generates Python code
    3. Executes code safely on Excel data
    4. Returns results with explanation
    
    Includes retry logic and error recovery for 90%+ success rate.
    
    Args:
        report_id: ID of the report to analyze
        query: Natural language query
        token: Authentication token
        db: Database session
        
    Returns:
        AgenticResponse with code, results, and explanation
    """
    # Authenticate
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if Excel file exists
    if not report.excel_path or not os.path.exists(report.excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found"
        )
    
    # Load financial data for context
    with open(report.extracted_data_path, 'r') as f:
        data = json.load(f)
    
    financial_data = data.get('financial_data', {})
    
    try:
        # Perform agentic analysis
        result = agentic_analyst.analyze(
            query.query,
            report.excel_path,
            financial_data
        )
        
        return AgenticResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis error: {str(e)}"
        )


@router.post("/agent/execute-code/{report_id}")
async def execute_custom_code(
    report_id: int,
    code: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Execute custom Python code on report data (advanced users)
    
    This endpoint allows power users to execute their own Python code
    on the Excel data. Use with caution - code is executed in a sandbox.
    
    Available DataFrames in code scope:
    - income_statement
    - balance_sheet
    - cash_flow
    - segments
    - geographic
    - key_metrics
    
    Args:
        report_id: ID of the report
        code: Python code to execute (must set 'result' variable)
        token: Authentication token
        db: Database session
        
    Returns:
        Dictionary with success status and result/error
    """
    user = auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if not report.excel_path or not os.path.exists(report.excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found"
        )
    
    try:
        # Load Excel data
        df_dict = agentic_analyst._load_excel_sheets(report.excel_path)
        
        # Execute code
        result = agentic_analyst._execute_code(code, df_dict)
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== Legacy Endpoints (Backward Compatibility) ====================

@router.post("/financial", response_model=ChatResponse)
def financial_chatbot(
    request: ChatRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Financial chatbot (legacy endpoint)
    
    This endpoint is maintained for backward compatibility.
    New implementations should use POST /chat/{report_id}
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get analysis
    analysis = db.query(Analysis).filter(
        Analysis.id == request.analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if not analysis.extracted_data:
        raise HTTPException(status_code=400, detail="No data available for this analysis")
    
    # Process chat request with history
    result = chatbot_service.chat(
        user_message=request.message,
        financial_data=analysis.extracted_data,
        chat_history=request.chat_history
    )
    
    return ChatResponse(
        answer=result["answer"],
        chat_history=result["chat_history"],
        context={"analysis_id": analysis.id}
    )


@router.post("/agentic", response_model=AgenticResponse)
def agentic_analyst_endpoint(
    request: AgenticRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Agentic analyst (legacy endpoint)
    
    This endpoint is maintained for backward compatibility.
    New implementations should use POST /agent/analyze/{report_id}
    """
    # Authenticate user
    current_user = auth_service.get_current_user(db, token)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )
    
    # Get report
    report = db.query(Report).filter(
        Report.id == request.report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.excel_path:
        raise HTTPException(status_code=400, detail="No Excel file available for this report")
    
    if not report.extracted_data:
        raise HTTPException(status_code=400, detail="No extracted data available")
    
    # Process with agentic analyst
    result = agentic_analyst.analyze(
        user_query=request.query,
        excel_path=report.excel_path,
        financial_data=report.extracted_data
    )
    
    return AgenticResponse(**result)
