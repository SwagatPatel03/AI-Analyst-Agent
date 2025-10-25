import { AlertCircle, Bot, CheckCircle, Code, Loader, PlayCircle, Sparkles, TrendingUp, Zap } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { useParams } from 'react-router-dom';
import { agentService } from '../../services/agentService';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import { SkeletonCard } from '../Skeleton';
import './AgentPage.css';
import ReportLayout from './ReportLayout';

interface Analysis {
  id: string;
  query: string;
  code: string;
  result: string;
  explanation: string;
  timestamp: Date;
  status: 'running' | 'success' | 'error';
}

const AgentPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const analysesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Sample starter queries
  const starterQueries = [
    "Calculate year-over-year revenue growth percentage",
    "Identify top 3 expense categories and their trends",
    "Compare profit margins across quarters",
    "Analyze cash flow patterns and predict next quarter",
  ];

  useEffect(() => {
    fetchReport();
  }, [reportId]);

  useEffect(() => {
    // Add welcome message after report is loaded
    if (report) {
      setAnalyses([
        {
          id: '1',
          query: '',
          code: '',
          result: '',
          explanation: `Welcome to the AI Agent! I can generate and execute Python code to perform deep financial analysis on ${report.company_name}'s data. Ask me to calculate metrics, create visualizations, or run custom analysis.`,
          timestamp: new Date(),
          status: 'success',
        },
      ]);
    }
  }, [report]);

  useEffect(() => {
    scrollToBottom();
  }, [analyses]);

  useEffect(() => {
    // Auto-resize textarea as user types
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputQuery]);

  const fetchReport = async () => {
    if (!reportId) return;

    try {
      setLoading(true);
      const reports = await reportService.getReports();
      const foundReport = reports.reports.find((r: Report) => r.id.toString() === reportId);
      
      if (foundReport) {
        setReport(foundReport);
      }
    } catch (err) {
      console.error('Failed to fetch report:', err);
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    analysesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleRunAnalysis = async () => {
    if (!inputQuery.trim() || isAnalyzing || !reportId) return;

    const userAnalysis: Analysis = {
      id: Date.now().toString(),
      query: inputQuery.trim(),
      code: '',
      result: '',
      explanation: '',
      timestamp: new Date(),
      status: 'running',
    };

    setAnalyses(prev => [...prev, userAnalysis]);
    setInputQuery('');
    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await agentService.analyzeWithAgent(parseInt(reportId), inputQuery.trim());
      
      const completedAnalysis: Analysis = {
        id: userAnalysis.id,
        query: inputQuery.trim(),
        code: response.generated_code || '',
        result: JSON.stringify(response.execution_result, null, 2),
        explanation: response.explanation || '',
        timestamp: new Date(),
        status: 'success',
      };

      setAnalyses(prev => prev.map(a => a.id === userAnalysis.id ? completedAnalysis : a));
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to execute analysis. Please try again.');
      
      const errorAnalysis: Analysis = {
        id: userAnalysis.id,
        query: inputQuery.trim(),
        code: '',
        result: '',
        explanation: "I apologize, but I encountered an error while processing your request. Please try rephrasing your query or try again.",
        timestamp: new Date(),
        status: 'error',
      };
      
      setAnalyses(prev => prev.map(a => a.id === userAnalysis.id ? errorAnalysis : a));
    } finally {
      setIsAnalyzing(false);
      inputRef.current?.focus();
    }
  };

  const handleStarterQuery = (query: string) => {
    setInputQuery(query);
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleRunAnalysis();
    }
    // Shift+Enter will naturally create a new line in textarea
  };

  if (loading) {
    return (
      <ReportLayout report={report || {} as Report}>
        <div className="agent-page">
          <SkeletonCard />
        </div>
      </ReportLayout>
    );
  }

  if (!report) {
    return (
      <ReportLayout report={{} as Report}>
        <div className="agent-page">
          <div className="agent-error">
            <AlertCircle className="error-icon" />
            <p>Report not found</p>
          </div>
        </div>
      </ReportLayout>
    );
  }

  return (
    <ReportLayout report={report}>
      <div className="agent-page">
        {/* Agent Header */}
        <div className="agent-header">
          <div className="agent-header::before" />
          <div className="agent-header-left">
            <div className="agent-header-icon">
              <Zap className="icon" />
            </div>
            <div className="agent-header-text">
              <h2 className="agent-header-title">AI Agent</h2>
              <p className="agent-header-subtitle">
                Code Generation & Execution
              </p>
            </div>
          </div>
          <div className="agent-status">
            <div className="status-indicator" />
            <span>Ready to analyze</span>
          </div>
        </div>

        {/* Analyses Display */}
        <div className="agent-analyses-container">
          <div className="agent-analyses">
            {analyses.map((analysis) => (
              <div key={analysis.id}>
                {/* User Query */}
                {analysis.query && (
                  <div className="analysis-query">
                    <div className="query-icon">
                      <PlayCircle />
                    </div>
                    <div className="query-content">
                      <p>{analysis.query}</p>
                      <span className="query-time">
                        {analysis.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                )}

                {/* Agent Response */}
                <div className={`analysis-response status-${analysis.status}`}>
                  <div className="response-icon">
                    {analysis.status === 'running' && <Loader className="icon-spin" />}
                    {analysis.status === 'success' && <Bot />}
                    {analysis.status === 'error' && <AlertCircle />}
                  </div>
                  <div className="response-content">
                    {/* Status Badge */}
                    {analysis.status === 'running' && (
                      <div className="status-badge running">
                        <Loader className="badge-icon" />
                        <span>Analyzing...</span>
                      </div>
                    )}
                    {analysis.status === 'success' && (
                      <div className="status-badge success">
                        <CheckCircle className="badge-icon" />
                        <span>Analysis Complete</span>
                      </div>
                    )}
                    {analysis.status === 'error' && (
                      <div className="status-badge error">
                        <AlertCircle className="badge-icon" />
                        <span>Error</span>
                      </div>
                    )}

                    {/* Generated Code */}
                    {analysis.code && (
                      <div className="code-section">
                        <div className="code-header">
                          <Code className="code-icon" />
                          <span>Generated Code</span>
                        </div>
                        <pre className="code-block">
                          <code>{analysis.code}</code>
                        </pre>
                      </div>
                    )}

                    {/* Execution Result */}
                    {analysis.result && (
                      <div className="result-section">
                        <div className="result-header">
                          <TrendingUp className="result-icon" />
                          <span>Results</span>
                        </div>
                        <pre className="result-block">
                          <code>{analysis.result}</code>
                        </pre>
                      </div>
                    )}

                    {/* Explanation */}
                    {analysis.explanation && (
                      <div className="explanation-section">
                        <ReactMarkdown>{analysis.explanation}</ReactMarkdown>
                      </div>
                    )}

                    <span className="response-time">
                      {analysis.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isAnalyzing && (
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            )}

            <div ref={analysesEndRef} />
          </div>
        </div>

        {/* Starter Queries */}
        {analyses.length === 1 && !isAnalyzing && (
          <div className="starter-queries">
            <p className="starter-queries-title">
              <Sparkles className="sparkles-icon" />
              Try asking:
            </p>
            <div className="starter-queries-grid">
              {starterQueries.map((query, index) => (
                <button
                  key={index}
                  onClick={() => handleStarterQuery(query)}
                  className="starter-query-btn"
                >
                  <Zap className="query-icon" />
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="agent-error">
            <p>{error}</p>
          </div>
        )}

        {/* Input Area */}
        <div className="agent-input-container">
          <div className="agent-input-wrapper">
            <textarea
              ref={inputRef}
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Describe the analysis you want to perform..."
              className="agent-input"
              disabled={isAnalyzing}
              rows={1}
            />
            <button
              onClick={handleRunAnalysis}
              disabled={!inputQuery.trim() || isAnalyzing}
              className="agent-run-btn"
            >
              <PlayCircle className="run-icon" />
              <span>Run Analysis</span>
            </button>
          </div>
          <p className="agent-input-hint">
            Press <kbd>Enter</kbd> to run • <kbd>Shift + Enter</kbd> for new line
          </p>
        </div>
      </div>
    </ReportLayout>
  );
};

export default AgentPage;
