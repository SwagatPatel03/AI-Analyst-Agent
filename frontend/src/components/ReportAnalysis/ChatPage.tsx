import { Bot, Send, Sparkles, TrendingUp, User } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { useParams } from 'react-router-dom';
import { chatService } from '../../services/chatService';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import { SkeletonCard } from '../Skeleton';
import './ChatPage.css';
import ReportLayout from './ReportLayout';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const ChatPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Sample starter questions
  const starterQuestions = [
    "What are the key financial highlights?",
    "How did revenue change compared to last year?",
    "What are the main risk factors?",
    "Analyze the profit margins",
  ];

  useEffect(() => {
    fetchReport();
  }, [reportId]);

  useEffect(() => {
    // Add welcome message after report is loaded
    if (report) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `Hello! I'm your AI Financial Analyst for ${report.company_name}. Ask me anything about this company's financial report, and I'll provide detailed insights backed by the data.`,
          timestamp: new Date(),
        },
      ]);
    }
  }, [report]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-resize textarea as user types
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputMessage]);

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
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !reportId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatService.chat(parseInt(reportId), inputMessage.trim());
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setError('Failed to get response. Please try again.');
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I apologize, but I encountered an error processing your request. Please try again.",
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
    // Shift+Enter will naturally create a new line in textarea
  };

  const handleStarterQuestion = (question: string) => {
    setInputMessage(question);
    inputRef.current?.focus();
  };

  if (loading) {
    return (
      <div className="chat-page">
        <SkeletonCard />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="chat-page">
        <div className="chat-error">
          <p>Report not found</p>
        </div>
      </div>
    );
  }

  return (
    <ReportLayout report={report}>
    <div className="chat-page">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-header-icon">
            <Bot className="icon" />
          </div>
          <div className="chat-header-text">
            <h2 className="chat-header-title">
              💬 AI Financial Analyst
            </h2>
            <p className="chat-header-subtitle">
              Ask questions about financial data, trends, and insights
            </p>
          </div>
        </div>
        <div className="chat-status">
          <span className="status-indicator"></span>
          <span className="status-text">Online</span>
        </div>
      </div>

      {/* Messages Container */}
      <div className="chat-messages-container">
        <div className="chat-messages">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat-message ${message.role === 'user' ? 'chat-message-user' : 'chat-message-assistant'}`}
            >
              <div className="message-avatar">
                {message.role === 'user' ? (
                  <User className="avatar-icon" />
                ) : (
                  <Bot className="avatar-icon" />
                )}
              </div>
              <div className="message-content">
                <div className="message-bubble">
                  <div className="message-text">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                </div>
                <span className="message-timestamp">
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="chat-message chat-message-assistant">
              <div className="message-avatar">
                <Bot className="avatar-icon" />
              </div>
              <div className="message-content">
                <div className="message-bubble">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Starter Questions */}
        {messages.length === 1 && (
          <div className="starter-questions">
            <p className="starter-questions-title">
              <Sparkles className="sparkles-icon" />
              Try asking:
            </p>
            <div className="starter-questions-grid">
              {starterQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleStarterQuestion(question)}
                  className="starter-question-btn"
                >
                  <TrendingUp className="question-icon" />
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="chat-error">
          <p>{error}</p>
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask me anything about this financial report..."
            className="chat-input"
            disabled={isLoading}
            rows={1}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="chat-send-btn"
          >
            <Send className="send-icon" />
          </button>
        </div>
        <p className="chat-input-hint">
          Press <kbd>Enter</kbd> to send • <kbd>Shift + Enter</kbd> for new line
        </p>
      </div>
    </div>
    </ReportLayout>
  );
};

export default ChatPage;
