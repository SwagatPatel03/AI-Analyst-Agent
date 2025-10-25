import {
  AlertCircle,
  ArrowLeft,
  BarChart3,
  CheckCircle,
  Download,
  ExternalLink,
  FileText,
  Info,
  Mail,
  MessageSquare,
  Send,
  Sparkles,
  Trash2,
  TrendingUp
} from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import { reportService } from '../../services/reportService';
import type { AgenticAnalysisResult, ChatMessage as APIChatMessage, LeadAnalysis, Predictions, Report } from '../../types';
import { getErrorMessage } from '../../utils/helpers';
import CustomVisualizationBuilder from './CustomVisualizationBuilder';

interface AnalysisViewProps {
  report: Report;
  onBack: () => void;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const AnalysisView: React.FC<AnalysisViewProps> = ({ report, onBack }) => {
  type TabId = 'overview' | 'visualizations' | 'predictions' | 'chat' | 'agent' | 'email';
  const [activeTab, setActiveTab] = useState<TabId>('overview');
  const [visualizations, setVisualizations] = useState<string[]>([]);
  const [customVisualizations, setCustomVisualizations] = useState<string[]>([]);
  const [predictions, setPredictions] = useState<Predictions | null>(null);
  const [reportSummary, setReportSummary] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [agentQuery, setAgentQuery] = useState('');
  const [agentResult, setAgentResult] = useState<AgenticAnalysisResult | null>(null);
  const [emailAddresses, setEmailAddresses] = useState('');
  const [includeLeadAnalysis, setIncludeLeadAnalysis] = useState(false);
  const [leadAnalysis, setLeadAnalysis] = useState<LeadAnalysis | null>(null);
  const [investmentLeads, setInvestmentLeads] = useState<any>(null);
  const [investorEmails, setInvestorEmails] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showCustomBuilder, setShowCustomBuilder] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Format analysis output with proper styling
  const formatAnalysisOutput = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, index) => {
      // Headings with === markers
      if (line.trim().startsWith('===') && line.trim().endsWith('===')) {
        const heading = line.replace(/===/g, '').trim();
        return (
          <h3 key={index} className="pb-2 mt-4 mb-3 text-lg font-bold text-blue-900 border-b-2 border-blue-300">
            {heading}
          </h3>
        );
      }
      
      // Section headings (all caps without ===)
      if (line.trim() && line.trim() === line.trim().toUpperCase() && line.trim().length < 50 && !line.includes(':')) {
        return (
          <h4 key={index} className="mt-3 mb-2 font-semibold text-gray-800 text-md">
            {line.trim()}
          </h4>
        );
      }
      
      // Key-value pairs (contains colon)
      if (line.includes(':') && !line.trim().startsWith('//')) {
        const [key, ...valueParts] = line.split(':');
        const value = valueParts.join(':').trim();
        return (
          <div key={index} className="flex items-baseline py-1">
            <span className="mr-2 font-medium text-gray-700">{key.trim()}:</span>
            <span className="text-gray-900">{value}</span>
          </div>
        );
      }
      
      // Empty lines
      if (line.trim() === '') {
        return <div key={index} className="h-2"></div>;
      }
      
      // Regular text
      return (
        <p key={index} className="py-1 text-gray-800">
          {line}
        </p>
      );
    });
  };

  useEffect(() => {
    if (activeTab === 'overview' && !reportSummary) {
      loadReportSummary();
    } else if (activeTab === 'visualizations' && visualizations.length === 0) {
      loadVisualizations();
      loadCustomVisualizations();
    } else if (activeTab === 'predictions' && !predictions) {
      loadPredictions();
    } else if (activeTab === 'chat' && chatMessages.length === 0) {
      loadChatHistory();
    }
  }, [activeTab]);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadVisualizations = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get existing visualizations
      const data = await reportService.getVisualizations(report.id);
      console.log('📊 Visualizations loaded:', data);
      console.log('📊 Visualizations array:', data.visualizations);
      console.log('📊 Array length:', data.visualizations?.length);
      
      // Convert to array - handle both array and object formats
      let vizArray: string[] = [];
      if (Array.isArray(data.visualizations)) {
        vizArray = data.visualizations;
      } else if (data.visualizations && typeof data.visualizations === 'object') {
        // If it's an object/dict, extract the values
        vizArray = Object.values(data.visualizations);
        console.log('📊 Converted object to array:', vizArray);
      }
      
      setVisualizations(vizArray);
    } catch (err: unknown) {
      console.error('❌ Failed to load visualizations:', err);
      setError('Failed to load visualizations: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadCustomVisualizations = async () => {
    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/analysis/custom-visualizations/${report.id}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setCustomVisualizations(data.custom_visualizations || []);
      }
    } catch (err: unknown) {
      console.error('Failed to load custom visualizations:', err);
    }
  };

  const loadReportSummary = async () => {
    try {
      const data = await reportService.getReportSummary(report.id);
      setReportSummary(data.report_summary);
    } catch {
      // Silent fail - summary might not be generated yet
    }
  };

  const generateVisualizations = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Generate new visualizations
      const generateResult = await reportService.generateVisualizations(report.id);
      console.log('🎨 Generate result:', generateResult);
      
      // Fetch the generated visualizations
      const data = await reportService.getVisualizations(report.id);
      console.log('📊 Get visualizations result:', data);
      
      // Convert to array - handle both array and object formats
      let vizArray: string[] = [];
      if (Array.isArray(data.visualizations)) {
        vizArray = data.visualizations;
      } else if (data.visualizations && typeof data.visualizations === 'object') {
        // If it's an object/dict, extract the values
        vizArray = Object.values(data.visualizations);
        console.log('📊 Converted object to array:', vizArray);
      }
      
      console.log('📊 Setting visualizations array:', vizArray);
      setVisualizations(vizArray);
      setSuccess('Visualizations generated successfully!');
    } catch (err: unknown) {
      console.error('❌ Generate visualizations error:', err);
      setError('Failed to generate visualizations: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadPredictions = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Get existing predictions
      const data = await reportService.getPredictions(report.id);
      console.log('📈 Predictions loaded:', data);
      console.log('📈 Predictions data:', data.predictions);
      setPredictions(data.predictions);
    } catch (err: unknown) {
      console.error('❌ Failed to load predictions:', err);
      setError('Failed to load predictions: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const generatePredictions = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Generate new predictions
      const data = await reportService.generatePredictions(report.id);
      console.log('📈 Generate predictions result:', data);
      console.log('📈 Predictions data:', data.predictions);
      setPredictions(data.predictions);
      setSuccess('Predictions generated successfully!');
    } catch (err: unknown) {
      console.error('❌ Generate predictions error:', err);
      setError('Failed to generate predictions: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      // Generate report
      await reportService.generateReport(report.id);
      
      // Load the generated summary
      await loadReportSummary();
      
      setSuccess('Executive summary generated successfully! ✨');
    } catch (err: unknown) {
      console.error('❌ Failed to generate report:', err);
      setError('Failed to generate report: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      setLoading(true);
      setError('');
      
      const blob = await reportService.downloadReportPDF(report.id);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Financial_Report_${report.company_name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSuccess('PDF downloaded successfully! 📄');
    } catch (err: unknown) {
      console.error('❌ Failed to download PDF:', err);
      setError('Failed to download PDF: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const loadChatHistory = async () => {
    try {
      const data = await reportService.getChatHistory(report.id);
      const messages = data.chat_history.map((msg: APIChatMessage) => ({
        ...msg,
        timestamp: new Date()
      }));
      setChatMessages(messages);
    } catch (err: unknown) {
      console.error('Failed to load chat history:', err);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setLoading(true);

    try {
      const response = await reportService.sendChatMessage(report.id, chatInput);
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (err: unknown) {
      setError('Chat error: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (window.confirm('Are you sure you want to clear chat history?')) {
      try {
        await reportService.clearChatHistory(report.id);
        setChatMessages([]);
        setSuccess('Chat history cleared');
      } catch {
        setError('Failed to clear chat history');
      }
    }
  };

  const handleAgentQuery = async () => {
    if (!agentQuery.trim()) return;

    setLoading(true);
    setError('');
    setAgentResult(null);

    try {
      const result = await reportService.agenticAnalysis(report.id, agentQuery);
      setAgentResult(result);
      if (!result.success) {
        setError(result.error || 'Analysis failed');
      }
    } catch (err: unknown) {
      setError('Agent error: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadExcel = async () => {
    try {
      const blob = await reportService.downloadExcel(report.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${report.company_name}_financial_data.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setSuccess('Excel file downloaded successfully');
    } catch (err: unknown) {
      setError('Download failed: ' + getErrorMessage(err));
    }
  };

  const handleSendEmail = async () => {
    if (!emailAddresses.trim()) {
      setError('Please enter at least one email address');
      return;
    }

    const emails = emailAddresses.split(',').map(e => e.trim()).filter(e => e);
    
    if (emails.length === 0) {
      setError('Please enter valid email addresses');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await reportService.sendEmail(report.id, emails, includeLeadAnalysis);
      setSuccess(`Email sent successfully to ${emails.length} recipient(s)`);
      setEmailAddresses('');
    } catch (err: unknown) {
      setError('Email send failed: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateLeads = async () => {
    setLoading(true);
    setError('');

    try {
      const data = await reportService.generateLeads(report.id);
      setLeadAnalysis(data.lead_analysis);
    } catch (err: unknown) {
      setError('Lead generation failed: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInvestmentLeads = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await reportService.generateInvestmentLeads(report.id);
      setInvestmentLeads(data);
      setSuccess('Investment opportunities generated successfully!');
    } catch (err: unknown) {
      setError('Failed to generate investment leads: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleExtractDepartmentLeads = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const result = await reportService.extractDepartmentLeads(report.id, true);
      
      if (result.success) {
        setSuccess(
          `✅ ${result.message}\n` +
          `📧 Email sent to: swagatpatel03@gmail.com\n` +
          `📊 ${result.leads.departments.length} department(s) analyzed`
        );
        
        // Optionally store the leads data for display
        console.log('Department Leads:', result.leads);
      } else {
        setError('Failed to extract department leads');
      }
    } catch (err: unknown) {
      setError('Department lead extraction failed: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleEmailInvestmentLeads = async (previewOnly: boolean) => {
    if (!investorEmails.trim()) {
      setError('Please enter at least one email address');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const emails = investorEmails.split(',').map(e => e.trim()).filter(e => e);
      const result = await reportService.emailInvestmentLeads(report.id, emails, previewOnly);

      if (previewOnly) {
        // Open preview in new window
        const previewWindow = window.open('', '_blank');
        if (previewWindow) {
          previewWindow.document.write(result.html_preview);
          previewWindow.document.close();
        }
        setSuccess('Email preview opened in new window');
      } else {
        setSuccess(`Investment leads emailed to ${emails.length} recipient(s)!`);
      }
    } catch (err: unknown) {
      setError('Failed to email investment leads: ' + getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const getRatingColor = (rating: string) => {
    if (rating.includes('Strong Buy') || rating.includes('Buy')) return 'text-green-600';
    if (rating.includes('Hold')) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPotentialBadge = (potential: string) => {
    if (potential === 'High') return 'bg-green-100 text-green-800';
    if (potential === 'Medium') return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getSeverityBadge = (severity: string) => {
    if (severity === 'High') return 'bg-red-100 text-red-800';
    if (severity === 'Medium') return 'bg-orange-100 text-orange-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getImpactBadge = (impact: string) => {
    if (impact === 'High') return 'bg-purple-100 text-purple-800';
    if (impact === 'Medium') return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white shadow-md">
        <div className="px-4 py-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center flex-1">
              <button
                onClick={onBack}
                className="p-2 mr-4 transition-colors rounded-lg hover:bg-gray-100"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900">{report.company_name}</h1>
                <p className="text-sm text-gray-500">
                  Year: {report.report_year || 'N/A'} • Uploaded: {new Date(report.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <button
              onClick={handleDownloadExcel}
              className="flex items-center px-4 py-2 text-white transition-all rounded-lg shadow-md bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 hover:shadow-lg"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Excel
            </button>
          </div>
        </div>
      </header>

      {/* Notification Messages */}
      {error && (
        <div className="px-4 mx-auto mt-4 max-w-7xl sm:px-6 lg:px-8">
          <div className="flex items-start p-4 border border-red-200 rounded-lg bg-red-50">
            <AlertCircle className="h-5 w-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-red-800">{error}</p>
            </div>
            <button onClick={() => setError('')} className="text-red-400 hover:text-red-600">
              <span className="text-xl">×</span>
            </button>
          </div>
        </div>
      )}

      {success && (
        <div className="px-4 mx-auto mt-4 max-w-7xl sm:px-6 lg:px-8">
          <div className="flex items-start p-4 border border-green-200 rounded-lg bg-green-50">
            <CheckCircle className="h-5 w-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-green-800">{success}</p>
            </div>
            <button onClick={() => setSuccess('')} className="text-green-400 hover:text-green-600">
              <span className="text-xl">×</span>
            </button>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white border-b sticky top-[73px] z-10">
        <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {([
              { id: 'overview', label: 'Overview', icon: FileText },
              { id: 'visualizations', label: 'Charts', icon: BarChart3 },
              { id: 'predictions', label: 'Predictions', icon: TrendingUp },
              { id: 'chat', label: 'Chatbot', icon: MessageSquare },
              { id: 'agent', label: 'AI Agent', icon: Sparkles },
              { id: 'email', label: 'Email & Leads', icon: Mail },
            ] as Array<{ id: 'overview' | 'visualizations' | 'predictions' | 'chat' | 'agent' | 'email'; label: string; icon: React.ComponentType<{ className?: string }> }>).map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setError('');
                  setSuccess('');
                }}
                className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-5 h-5 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">
        
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="p-6 bg-white shadow-md rounded-xl">
              <h2 className="flex items-center mb-6 text-2xl font-bold">
                <FileText className="w-6 h-6 mr-2 text-primary-600" />
                Report Overview
              </h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="p-4 border border-blue-200 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100">
                  <p className="mb-1 text-sm font-medium text-blue-600">Company</p>
                  <p className="text-lg font-bold text-gray-900">{report.company_name}</p>
                </div>
                <div className="p-4 border border-purple-200 rounded-lg bg-gradient-to-br from-purple-50 to-purple-100">
                  <p className="mb-1 text-sm font-medium text-purple-600">Report Year</p>
                  <p className="text-lg font-bold text-gray-900">{report.report_year || 'N/A'}</p>
                </div>
                <div className="p-4 border border-green-200 rounded-lg bg-gradient-to-br from-green-50 to-green-100">
                  <p className="mb-1 text-sm font-medium text-green-600">Status</p>
                  <p className="text-lg font-bold text-gray-900 capitalize">{report.status}</p>
                </div>
                <div className="p-4 border border-orange-200 rounded-lg bg-gradient-to-br from-orange-50 to-orange-100">
                  <p className="mb-1 text-sm font-medium text-orange-600">Uploaded</p>
                  <p className="text-lg font-bold text-gray-900">
                    {new Date(report.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Executive Summary Section */}
            <div className="p-6 bg-white shadow-md rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="flex items-center text-xl font-bold">
                  <Sparkles className="w-6 h-6 mr-2 text-yellow-500" />
                  AI-Generated Executive Summary
                </h3>
                <div className="flex items-center gap-3">
                  <span className="px-3 py-1 text-xs font-semibold text-blue-700 bg-blue-100 rounded-full">
                    Powered by Gemini AI
                  </span>
                </div>
              </div>
              
              {reportSummary ? (
                // Report exists - show download button only
                <div className="flex items-center justify-center p-8 border-2 border-blue-300 border-dashed rounded-lg bg-gradient-to-r from-blue-50 to-purple-50">
                  <div className="text-center">
                    <FileText className="w-16 h-16 mx-auto mb-4 text-blue-500" />
                    <p className="mb-2 text-lg font-semibold text-gray-800">
                      Executive Summary Report Ready
                    </p>
                    <p className="mb-6 text-sm text-gray-600">
                      Download the full comprehensive report with detailed financial analysis
                    </p>
                    <button
                      onClick={handleDownloadPDF}
                      disabled={loading}
                      className="flex items-center px-6 py-3 mx-auto font-semibold text-white transition-all rounded-lg shadow-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Download className="w-5 h-5 mr-2" />
                      Download Report (PDF)
                    </button>
                  </div>
                </div>
              ) : (
                // No report - show generate button
                <div className="p-8 text-center border-2 border-gray-300 border-dashed rounded-lg bg-gradient-to-br from-gray-50 to-blue-50">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p className="mb-2 text-lg font-medium text-gray-700">No Executive Summary Available</p>
                  <p className="mb-6 text-sm text-gray-500">
                    Generate a concise AI summary to skip reading the full report
                  </p>
                  <button
                    onClick={handleGenerateReport}
                    disabled={loading}
                    className="px-6 py-3 font-semibold text-white transition-all rounded-lg shadow-lg bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? '⏳ Generating...' : '✨ Generate Executive Summary'}
                  </button>
                </div>
              )}
            </div>

            <div className="p-6 bg-white shadow-md rounded-xl">
              <h3 className="mb-4 text-xl font-bold">Quick Actions</h3>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <button
                  onClick={() => setActiveTab('visualizations')}
                  className="flex items-center justify-center p-4 transition-all border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50"
                >
                  <BarChart3 className="w-6 h-6 mr-3 text-primary-600" />
                  <span className="font-medium">View Charts</span>
                </button>
                <button
                  onClick={() => setActiveTab('predictions')}
                  className="flex items-center justify-center p-4 transition-all border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50"
                >
                  <TrendingUp className="w-6 h-6 mr-3 text-green-600" />
                  <span className="font-medium">Get Predictions</span>
                </button>
                <button
                  onClick={() => setActiveTab('chat')}
                  className="flex items-center justify-center p-4 transition-all border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50"
                >
                  <MessageSquare className="w-6 h-6 mr-3 text-blue-600" />
                  <span className="font-medium">Ask Questions</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Visualizations Tab */}
        {activeTab === 'visualizations' && (
          <div className="space-y-6">
            {loading ? (
              <div className="p-12 text-center bg-white shadow-md rounded-xl">
                <div className="w-16 h-16 mx-auto mb-4 border-b-4 rounded-full animate-spin border-primary-600"></div>
                <p className="font-medium text-gray-600">Generating visualizations...</p>
                <p className="mt-2 text-sm text-gray-500">This may take a few moments</p>
              </div>
            ) : visualizations.length === 0 ? (
              <div className="p-12 text-center bg-white shadow-md rounded-xl">
                <BarChart3 className="w-20 h-20 mx-auto mb-4 text-gray-300" />
                <p className="mb-6 text-lg text-gray-500">No visualizations available</p>
                <p className="mb-6 text-sm text-gray-400">Click the button below to generate interactive charts from your financial data</p>
                <button
                  onClick={generateVisualizations}
                  className="px-8 py-4 text-lg font-semibold text-white transition-colors bg-blue-600 rounded-lg shadow-lg hover:bg-blue-700 hover:shadow-xl"
                >
                  🎨 Generate Visualizations
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-start justify-between p-4 border border-blue-200 rounded-lg bg-blue-50">
                  <div className="flex items-start flex-1">
                    <Info className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-blue-800">
                      Interactive charts generated from your financial data. Hover over elements for detailed information.
                    </p>
                  </div>
                  <button
                    onClick={generateVisualizations}
                    disabled={loading}
                    className="px-6 py-2 ml-4 text-sm font-semibold text-white transition-colors bg-blue-600 rounded-lg shadow hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed whitespace-nowrap"
                  >
                    🔄 Regenerate
                  </button>
                </div>
                
                {/* Custom Visualization Builder Section */}
                <div className="overflow-hidden border-2 border-purple-200 rounded-xl">
                  <button
                    onClick={() => setShowCustomBuilder(!showCustomBuilder)}
                    className="flex items-center justify-between w-full px-6 py-4 font-semibold text-white transition-all bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                  >
                    <span className="flex items-center">
                      <Sparkles className="w-5 h-5 mr-2" />
                      Create Custom Visualization
                    </span>
                    <span className="px-3 py-1 text-sm rounded-full bg-white/20">
                      {showCustomBuilder ? '▼ Hide' : '▶ Show'}
                    </span>
                  </button>
                  
                  {showCustomBuilder && (
                    <div className="p-6 bg-gray-50">
                      <CustomVisualizationBuilder 
                        reportId={report.id}
                        onChartCreated={() => {
                          loadCustomVisualizations();
                          setSuccess('Custom chart created! 🎉');
                        }}
                      />
                    </div>
                  )}
                </div>
                
                {/* Custom Visualizations Section */}
                {customVisualizations.length > 0 && (
                  <div>
                    <h3 className="flex items-center mb-4 text-xl font-bold text-gray-800">
                      <Sparkles className="w-6 h-6 mr-2 text-purple-600" />
                      Your Custom Charts ({customVisualizations.length})
                    </h3>
                    <div className="space-y-4">
                      {customVisualizations.map((viz, idx) => {
                        const cleanPath = viz
                          .replace(/\\/g, '/')
                          .replace(/^outputs\//, '');
                        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                        const fullUrl = `${apiBaseUrl}/static/${cleanPath}`;
                        
                        return (
                          <div key={idx} className="overflow-hidden bg-white border-2 border-purple-100 shadow-md rounded-xl">
                            <div className="flex items-center justify-between p-4 border-b border-purple-200 bg-purple-50">
                              <h3 className="flex items-center font-semibold text-gray-900">
                                <span className="mr-2 text-purple-600">⭐</span>
                                Custom Chart {idx + 1}
                              </h3>
                              <a
                                href={fullUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center text-sm text-purple-600 hover:text-purple-700"
                              >
                                <ExternalLink className="w-4 h-4 mr-1" />
                                Open in new tab
                              </a>
                            </div>
                            <iframe
                              src={fullUrl}
                              className="w-full h-[500px] border-0"
                              title={`Custom Chart ${idx + 1}`}
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
                
                {/* Predefined Visualizations Section */}
                <div>
                  <h3 className="flex items-center mb-4 text-xl font-bold text-gray-800">
                    <BarChart3 className="w-6 h-6 mr-2 text-blue-600" />
                    Predefined Charts ({visualizations.length})
                  </h3>
                  <div className="space-y-4">
                    {Array.isArray(visualizations) && visualizations.map((viz, idx) => {
                      const cleanPath = viz
                        .replace(/\\/g, '/')
                        .replace(/^outputs\//, '');
                      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                      const fullUrl = `${apiBaseUrl}/static/${cleanPath}`;
                      
                      return (
                        <div key={idx} className="overflow-hidden bg-white shadow-md rounded-xl">
                          <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
                            <h3 className="font-semibold text-gray-900">Visualization {idx + 1}</h3>
                            <a
                              href={fullUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center text-sm text-primary-600 hover:text-primary-700"
                            >
                              <ExternalLink className="w-4 h-4 mr-1" />
                              Open in new tab
                            </a>
                          </div>
                          <iframe
                            src={fullUrl}
                            className="w-full h-[500px] border-0"
                            title={`Visualization ${idx + 1}`}
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Predictions Tab */}
        {activeTab === 'predictions' && (
          <div className="space-y-6">
            {loading ? (
              <div className="p-12 text-center bg-white shadow-md rounded-xl">
                <div className="w-16 h-16 mx-auto mb-4 border-b-4 rounded-full animate-spin border-primary-600"></div>
                <p className="font-medium text-gray-600">Generating predictions...</p>
                <p className="mt-2 text-sm text-gray-500">Analyzing financial data with ML models</p>
              </div>
            ) : predictions && predictions.growth_rate ? (
              <>
                {/* Growth Prediction */}
                <div className="p-8 border shadow-md bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl border-primary-200">
                  <h3 className="flex items-center mb-6 text-2xl font-bold">
                    <TrendingUp className="mr-2 h-7 w-7 text-primary-600" />
                    Growth Prediction
                  </h3>
                  <div className="flex items-center justify-center mb-6">
                    <div className="text-center">
                      <p className="mb-2 text-6xl font-bold text-primary-600">
                        {predictions.growth_rate.predicted}%
                      </p>
                      <p className="text-sm text-gray-600">Predicted Growth Rate</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                    <div className="p-4 text-center bg-white rounded-lg">
                      <p className="mb-1 text-sm text-gray-600">Lower Bound</p>
                      <p className="text-2xl font-bold text-gray-900">{predictions.growth_rate.confidence_lower}%</p>
                    </div>
                    <div className="p-4 text-center bg-white rounded-lg">
                      <p className="mb-1 text-sm text-gray-600">Confidence Level</p>
                      <p className="text-2xl font-bold text-gray-900">{(predictions.growth_rate.confidence_level * 100).toFixed(0)}%</p>
                    </div>
                    <div className="p-4 text-center bg-white rounded-lg">
                      <p className="mb-1 text-sm text-gray-600">Upper Bound</p>
                      <p className="text-2xl font-bold text-gray-900">{predictions.growth_rate.confidence_upper}%</p>
                    </div>
                  </div>
                </div>

                {/* Sales Forecast */}
                <div className="p-6 bg-white shadow-md rounded-xl">
                  <h3 className="flex items-center mb-4 text-xl font-bold">
                    <BarChart3 className="w-6 h-6 mr-2 text-green-600" />
                    Sales Forecast (Next 3 Years)
                  </h3>
                  <div className="space-y-3">
                    {predictions.sales_forecast?.map((forecast, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 border border-green-200 rounded-lg bg-gradient-to-r from-green-50 to-emerald-50">
                        <div>
                          <p className="font-semibold text-gray-900">Year {forecast.year}</p>
                          <p className="text-sm text-gray-600">Growth: {forecast.growth_rate}%</p>
                        </div>
                        <p className="text-xl font-bold text-green-600">
                          {forecast.predicted_revenue.toLocaleString()} {forecast.currency}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Segment Breakdown */}
                {predictions.segment_breakdown && predictions.segment_breakdown.length > 0 && (
                  <div className="p-6 bg-white shadow-md rounded-xl">
                    <h3 className="mb-4 text-xl font-bold">Segment Breakdown</h3>
                    <div className="space-y-3">
                      {predictions.segment_breakdown.map((segment, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg bg-gray-50">
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900">{segment.segment}</p>
                            <p className="text-sm text-gray-600">
                              Current: {segment.current_revenue.toLocaleString()} ({segment.proportion}%)
                            </p>
                          </div>
                          <div className="text-right">
                            <p className={`text-lg font-bold ${segment.predicted_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {segment.predicted_growth >= 0 ? '+' : ''}{segment.predicted_growth}%
                            </p>
                            <p className="text-xs text-gray-500">Predicted Growth</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                <div className="p-6 bg-white shadow-md rounded-xl">
                  <h3 className="flex items-center mb-4 text-xl font-bold">
                    <Info className="w-6 h-6 mr-2 text-blue-600" />
                    Investment Recommendations
                  </h3>
                  <ul className="space-y-3">
                    {predictions.recommendations?.map((rec, idx) => (
                      <li key={idx} className="flex items-start p-4 border border-blue-200 rounded-lg bg-blue-50">
                        <span className="flex items-center justify-center flex-shrink-0 w-6 h-6 mr-3 text-sm font-bold text-white bg-blue-600 rounded-full">
                          {idx + 1}
                        </span>
                        <span className="text-gray-800">{typeof rec === 'string' ? rec : rec.description}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            ) : predictions && predictions.success === false ? (
              // Handle error case - insufficient data
              <div className="p-12 text-center bg-white shadow-md rounded-xl">
                <div className="flex items-center justify-center w-20 h-20 mx-auto mb-6 bg-yellow-100 rounded-full">
                  <span className="text-5xl">⚠️</span>
                </div>
                <h3 className="mb-4 text-2xl font-bold text-gray-900">
                  {predictions.error || 'Unable to Generate Predictions'}
                </h3>
                
                {predictions.recommendations && predictions.recommendations.length > 0 && (
                  <div className="max-w-2xl mx-auto mt-8">
                    <h4 className="mb-4 text-lg font-semibold text-gray-800">Recommendations:</h4>
                    <div className="space-y-4 text-left">
                      {predictions.recommendations.map((rec, idx) => (
                        <div key={idx} className="p-4 border border-yellow-200 rounded-lg bg-yellow-50">
                          {typeof rec === 'string' ? (
                            <p className="text-sm text-gray-700">{rec}</p>
                          ) : (
                            <div className="flex items-start">
                              {rec.icon && <span className="mr-3 text-3xl">{rec.icon}</span>}
                              <div className="flex-1">
                                {rec.title && (
                                  <h5 className="mb-2 font-semibold text-gray-900">{rec.title}</h5>
                                )}
                                {rec.description && (
                                  <p className="mb-2 text-sm text-gray-700">{rec.description}</p>
                                )}
                                {rec.action && (
                                  <p className="text-xs font-medium text-blue-600">{rec.action}</p>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="max-w-xl p-4 mx-auto mt-6 border border-blue-200 rounded-lg bg-blue-50">
                  <p className="text-sm text-blue-800">
                    💡 <strong>Tip:</strong> Make sure your Excel file contains complete financial statements including revenue, expenses, balance sheet data, and key financial ratios for accurate ML predictions.
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-white shadow-md rounded-xl">
                <TrendingUp className="w-20 h-20 mx-auto mb-4 text-gray-300" />
                <p className="mb-6 text-lg text-gray-500">No predictions generated yet</p>
                <p className="mb-6 text-sm text-gray-400">Click the button below to generate ML-powered growth predictions and sales forecasts</p>
                <button
                  onClick={generatePredictions}
                  className="px-8 py-4 text-lg font-semibold text-white transition-colors bg-green-600 rounded-lg shadow-lg hover:bg-green-700 hover:shadow-xl"
                >
                  📈 Generate Predictions
                </button>
              </div>
            )}
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="bg-white rounded-xl shadow-md h-[calc(100vh-300px)] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="flex items-center text-lg font-bold">
                <MessageSquare className="w-5 h-5 mr-2 text-primary-600" />
                Financial Chatbot
              </h3>
              <button
                onClick={handleClearChat}
                className="flex items-center px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Clear History
              </button>
            </div>
            
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              {chatMessages.length === 0 ? (
                <div className="py-12 text-center">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="mb-2 text-gray-500">No messages yet</p>
                  <p className="text-sm text-gray-400">Ask a question about the financial report</p>
                </div>
              ) : (
                <>
                  {chatMessages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          msg.role === 'user'
                            ? 'bg-gradient-to-r from-primary-600 to-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <p className={`text-xs mt-2 ${msg.role === 'user' ? 'text-primary-100' : 'text-gray-500'}`}>
                          {msg.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </>
              )}
            </div>

            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                  placeholder="Ask about revenue, growth, metrics..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  disabled={loading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={loading || !chatInput.trim()}
                  className="px-6 py-3 text-white transition-all rounded-lg bg-gradient-to-r from-primary-600 to-blue-600 hover:from-primary-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* AI Agent Tab */}
        {activeTab === 'agent' && (
          <div className="space-y-6">
            <div className="p-6 border border-purple-200 shadow-md bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
              <h3 className="flex items-center mb-4 text-xl font-bold">
                <Sparkles className="w-6 h-6 mr-2 text-purple-600" />
                Agentic AI Analyst
              </h3>
              <p className="mb-6 text-gray-700">
                Advanced AI agent that can perform custom analysis, calculations, and generate insights using code execution.
              </p>
              
              <div className="space-y-4">
                <div>
                  <label className="block mb-2 text-sm font-semibold text-gray-700">
                    Analysis Query
                  </label>
                  <textarea
                    value={agentQuery}
                    onChange={(e) => setAgentQuery(e.target.value)}
                    placeholder="E.g., Calculate year-over-year revenue growth and compare with industry benchmarks..."
                    className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    disabled={loading}
                  />
                </div>

                <button
                  onClick={handleAgentQuery}
                  disabled={loading || !agentQuery.trim()}
                  className="flex items-center justify-center w-full px-6 py-4 text-white transition-all rounded-lg shadow-md bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg"
                >
                  {loading ? (
                    <>
                      <svg className="w-5 h-5 mr-3 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Run Analysis
                    </>
                  )}
                </button>
              </div>
            </div>

            {agentResult && (
              <div className="p-6 bg-white shadow-md rounded-xl">
                <h4 className="mb-4 text-lg font-bold">Analysis Results</h4>
                
                {agentResult.success ? (
                  <div className="space-y-4">
                    {agentResult.analysis && (
                      <div className="p-4 border border-green-200 rounded-lg bg-green-50">
                        <p className="mb-2 text-sm font-medium text-green-800">Analysis</p>
                        <p className="text-gray-800 whitespace-pre-wrap">{agentResult.analysis}</p>
                      </div>
                    )}
                    
                    {agentResult.code_executed && (
                      <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                        <p className="mb-2 text-sm font-medium text-gray-700">Code Executed</p>
                        <pre className="overflow-x-auto text-xs text-gray-800">{agentResult.code_executed}</pre>
                      </div>
                    )}
                    
                    {agentResult.result && (
                      <div className="p-6 border border-blue-200 rounded-lg bg-gradient-to-br from-white to-blue-50">
                        <div className="flex items-center mb-4">
                          <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                          <h3 className="text-lg font-bold text-blue-900">Analysis Results</h3>
                        </div>
                        
                        {/* Display formatted output */}
                        {typeof (agentResult.result as { output?: unknown }).output === 'string' && (
                          <div className="p-4 bg-white rounded-lg shadow-sm">
                            {formatAnalysisOutput((agentResult.result as { output?: string }).output!)}
                          </div>
                        )}
                        
                        {/* Display errors if they exist */}
                        {typeof (agentResult.result as { errors?: unknown }).errors === 'string' && (
                          <div className="p-4 mt-4 border border-red-200 rounded-lg bg-red-50">
                            <div className="flex items-center mb-2">
                              <AlertCircle className="w-4 h-4 mr-2 text-red-600" />
                              <span className="font-semibold text-red-800">Errors:</span>
                            </div>
                            <pre className="text-sm text-red-700 whitespace-pre-wrap">
                              {(agentResult.result as { errors?: string }).errors!}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                    <p className="text-sm text-red-800">{agentResult.error || 'Analysis failed'}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Email & Leads Tab */}
        {activeTab === 'email' && (
          <div className="space-y-6">
            
            {/* Department Leads Extraction - MOVED TO TOP FOR VISIBILITY */}
            <div className="p-6 bg-white shadow-md rounded-xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="flex items-center text-xl font-bold">
                  <Mail className="w-6 h-6 mr-2 text-orange-600" />
                  Department Leads Extraction
                </h3>
              </div>

              <div className="p-4 mb-4 border-2 border-orange-200 rounded-lg bg-orange-50">
                <div className="flex items-start">
                  <svg className="w-5 h-5 mt-0.5 mr-3 text-orange-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h4 className="mb-2 font-semibold text-orange-900">📊 Auto-Extract from Generated Excel</h4>
                    <p className="text-sm text-orange-800">
                      This feature analyzes the <strong>Excel file automatically generated</strong> from your uploaded report. 
                      It extracts department-wise leads including:
                    </p>
                    <ul className="mt-2 ml-4 text-sm text-orange-800 list-disc">
                      <li><strong>Growth indicators</strong> - revenue trends, expansion opportunities</li>
                      <li><strong>Status updates</strong> - current state of department work</li>
                      <li><strong>Work progress</strong> - ongoing projects and achievements</li>
                    </ul>
                    <p className="mt-3 text-sm font-semibold text-orange-900">
                      📧 Results will be emailed to: <span className="font-mono">swagatpatel03@gmail.com</span>
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleExtractDepartmentLeads}
                disabled={loading}
                className="flex items-center justify-center w-full px-6 py-4 text-white transition-all rounded-lg shadow-md bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg"
              >
                {loading ? (
                  <>
                    <svg className="w-5 h-5 mr-3 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Extracting Department Leads...
                  </>
                ) : (
                  <>
                    <Mail className="w-5 h-5 mr-2" />
                    Extract & Email Department Leads
                  </>
                )}
              </button>

              <div className="mt-4 text-sm text-gray-600">
                <p className="flex items-center">
                  <span className="mr-2">✅</span>
                  Uses auto-generated Excel from your report
                </p>
                <p className="flex items-center">
                  <span className="mr-2">🤖</span>
                  Powered by Groq AI for intelligent analysis
                </p>
                <p className="flex items-center">
                  <span className="mr-2">⚡</span>
                  One-click extraction and email delivery
                </p>
              </div>
            </div>

            {/* Send Email Section */}
            <div className="p-6 bg-white shadow-md rounded-xl">
              <h3 className="flex items-center mb-6 text-xl font-bold">
                <Mail className="w-6 h-6 mr-2 text-primary-600" />
                Send Report Email
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block mb-2 text-sm font-semibold text-gray-700">
                    Email Addresses <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={emailAddresses}
                    onChange={(e) => setEmailAddresses(e.target.value)}
                    placeholder="email1@example.com, email2@example.com"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled={loading}
                  />
                  <p className="mt-1 text-xs text-gray-500">Separate multiple emails with commas</p>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="includeLeads"
                    checked={includeLeadAnalysis}
                    onChange={(e) => setIncludeLeadAnalysis(e.target.checked)}
                    className="w-4 h-4 border-gray-300 rounded text-primary-600 focus:ring-primary-500"
                    disabled={loading}
                  />
                  <label htmlFor="includeLeads" className="ml-2 text-sm text-gray-700">
                    Include lead analysis in email
                  </label>
                </div>

                <button
                  onClick={handleSendEmail}
                  disabled={loading || !emailAddresses.trim()}
                  className="flex items-center justify-center w-full px-6 py-4 text-white transition-all rounded-lg shadow-md bg-gradient-to-r from-primary-600 to-blue-600 hover:from-primary-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg"
                >
                  {loading ? (
                    <>
                      <svg className="w-5 h-5 mr-3 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Sending Email...
                    </>
                  ) : (
                    <>
                      <Mail className="w-5 h-5 mr-2" />
                      Send Email
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Lead Analysis Section */}
            <div className="p-6 bg-white shadow-md rounded-xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="flex items-center text-xl font-bold">
                  <TrendingUp className="w-6 h-6 mr-2 text-green-600" />
                  Lead Scoring Analysis
                </h3>
                <button
                  onClick={handleGenerateLeads}
                  disabled={loading}
                  className="px-4 py-2 text-white transition-all bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  Generate Lead Analysis
                </button>
              </div>

              {leadAnalysis ? (
                <div className="space-y-4">
                  <div className={`p-6 rounded-lg border-2 ${getScoreBgColor(leadAnalysis.investment_score)}`}>
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-lg font-bold">Investment Score</h4>
                      <span className={`text-4xl font-bold ${getScoreColor(leadAnalysis.investment_score)}`}>
                        {leadAnalysis.investment_score}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700">{leadAnalysis.recommendation}</p>
                  </div>

                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="p-4 border border-green-200 rounded-lg bg-green-50">
                      <h4 className="mb-3 text-sm font-medium text-green-600">Key Strengths</h4>
                      <ul className="space-y-2">
                        {leadAnalysis.key_strengths.map((strength, idx) => (
                          <li key={idx} className="flex items-start text-sm text-gray-800">
                            <span className="mr-2 text-green-500">✓</span>
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                      <h4 className="mb-3 text-sm font-medium text-red-600">Risk Factors</h4>
                      <ul className="space-y-2">
                        {leadAnalysis.risk_factors.map((risk, idx) => (
                          <li key={idx} className="flex items-start text-sm text-gray-800">
                            <span className="mr-2 text-red-500">⚠</span>
                            <span>{risk}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div>
                    <h4 className="mb-3 font-bold">Action Items</h4>
                    <ul className="space-y-2">
                      {leadAnalysis.action_items.map((item, idx) => (
                        <li key={idx} className="flex items-start p-3 rounded-lg bg-gray-50">
                          <span className="flex items-center justify-center flex-shrink-0 w-6 h-6 mr-3 text-xs font-bold text-white rounded-full bg-primary-600">
                            {idx + 1}
                          </span>
                          <span className="text-sm text-gray-800">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center">
                  <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500">No lead analysis generated yet</p>
                  <p className="mt-2 text-sm text-gray-400">Click "Generate Lead Analysis" to start</p>
                </div>
              )}
            </div>

            {/* Investment Opportunities Section (NEW) */}
            <div className="p-6 bg-white shadow-md rounded-xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="flex items-center text-xl font-bold">
                  <Sparkles className="w-6 h-6 mr-2 text-purple-600" />
                  Investment Opportunities & Email
                </h3>
                <button
                  onClick={handleGenerateInvestmentLeads}
                  disabled={loading}
                  className="px-4 py-2 text-white transition-all bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
                >
                  {loading ? 'Generating...' : 'Generate Investment Leads'}
                </button>
              </div>

              {investmentLeads ? (
                <div className="space-y-6">
                  {/* Rating Badge */}
                  <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-sm font-medium text-gray-600">Investment Rating</h4>
                        <p className={`text-2xl font-bold mt-1 ${getRatingColor(investmentLeads.rating)}`}>
                          {investmentLeads.rating}
                        </p>
                      </div>
                      <div className="text-right">
                        <h4 className="text-sm font-medium text-gray-600">Company</h4>
                        <p className="mt-1 text-lg font-semibold text-gray-800">{investmentLeads.company}</p>
                      </div>
                    </div>
                    <p className="mt-3 text-sm text-gray-700">{investmentLeads.summary}</p>
                  </div>

                  {/* Opportunities */}
                  <div>
                    <h4 className="mb-3 text-lg font-bold text-green-700">📈 Investment Opportunities</h4>
                    <div className="space-y-3">
                      {investmentLeads.opportunities.map((opp: any, idx: number) => (
                        <div key={idx} className="p-4 border border-green-200 rounded-lg bg-green-50">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-semibold text-gray-800">{opp.title}</h5>
                            <div className="flex gap-2">
                              <span className={`px-2 py-1 text-xs rounded ${getPotentialBadge(opp.potential)}`}>
                                {opp.potential}
                              </span>
                              <span className="px-2 py-1 text-xs text-blue-700 bg-blue-100 rounded">
                                {opp.timeframe}
                              </span>
                            </div>
                          </div>
                          <p className="text-sm text-gray-700">{opp.evidence}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Risks */}
                  <div>
                    <h4 className="mb-3 text-lg font-bold text-red-700">⚠️ Risk Factors</h4>
                    <div className="space-y-3">
                      {investmentLeads.risks.map((risk: any, idx: number) => (
                        <div key={idx} className="p-4 border border-red-200 rounded-lg bg-red-50">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-semibold text-gray-800">{risk.title}</h5>
                            <span className={`px-2 py-1 text-xs rounded ${getSeverityBadge(risk.severity)}`}>
                              {risk.severity}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700">{risk.evidence}</p>
                          {risk.mitigation && (
                            <p className="mt-2 text-sm text-green-700">
                              <strong>Mitigation:</strong> {risk.mitigation}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Growth Catalysts */}
                  <div>
                    <h4 className="mb-3 text-lg font-bold text-purple-700">🚀 Growth Catalysts</h4>
                    <div className="space-y-3">
                      {investmentLeads.catalysts.map((catalyst: any, idx: number) => (
                        <div key={idx} className="p-4 border border-purple-200 rounded-lg bg-purple-50">
                          <div className="flex items-start justify-between mb-2">
                            <h5 className="font-semibold text-gray-800">{catalyst.title}</h5>
                            <span className={`px-2 py-1 text-xs rounded ${getImpactBadge(catalyst.impact)}`}>
                              {catalyst.impact}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700">{catalyst.evidence}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Email Section */}
                  <div className="p-4 border-2 border-purple-200 rounded-lg bg-purple-50">
                    <h4 className="mb-4 text-lg font-bold text-purple-900">📧 Email to Investors</h4>
                    <div className="space-y-3">
                      <input
                        type="text"
                        value={investorEmails}
                        onChange={(e) => setInvestorEmails(e.target.value)}
                        placeholder="investor@fund.com, analyst@firm.com"
                        className="w-full px-4 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        disabled={loading}
                      />
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleEmailInvestmentLeads(true)}
                          disabled={loading || !investorEmails.trim()}
                          className="flex items-center justify-center flex-1 px-4 py-2 text-purple-700 transition-all bg-white border-2 border-purple-300 rounded-lg hover:bg-purple-50 disabled:opacity-50"
                        >
                          Preview Email
                        </button>
                        <button
                          onClick={() => handleEmailInvestmentLeads(false)}
                          disabled={loading || !investorEmails.trim()}
                          className="flex items-center justify-center flex-1 px-4 py-2 text-white transition-all bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50"
                        >
                          <Send className="w-4 h-4 mr-2" />
                          Send Email
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center">
                  <Sparkles className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500">No investment opportunities generated yet</p>
                  <p className="mt-2 text-sm text-gray-400">
                    Click "Generate Investment Leads" to analyze opportunities, risks, and catalysts
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

      </main>
    </div>
  );
};

export default AnalysisView;
