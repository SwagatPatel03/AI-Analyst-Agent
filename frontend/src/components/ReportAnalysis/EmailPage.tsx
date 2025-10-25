import { AlertCircle, CheckCircle, Loader, Mail, Send, Sparkles, TrendingUp } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import { SkeletonCard } from '../Skeleton';
import './EmailPage.css';
import ReportLayout from './ReportLayout';

interface InvestmentLeads {
  company: string;
  summary: string;
  rating: string;
  opportunities: Array<{
    title: string;
    evidence: string;
    potential: string;
    timeframe: string;
  }>;
  risks: Array<{
    title: string;
    severity: string;
    evidence: string;
    mitigation?: string;
  }>;
  catalysts: Array<{
    title: string;
    impact: string;
    evidence: string;
  }>;
  key_metrics: Record<string, unknown>;
}

const EmailPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [investmentLeads, setInvestmentLeads] = useState<InvestmentLeads | null>(null);
  const [generatingLeads, setGeneratingLeads] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [emailRecipient, setEmailRecipient] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchReport();
  }, [reportId]);

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
      setError('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateLeads = async () => {
    if (!reportId) return;

    try {
      setGeneratingLeads(true);
      setError(null);
      setSuccess(null);

      // Use the NEW LLM-based investment leads endpoint
      const response = await reportService.generateInvestmentLeads(parseInt(reportId));
      setInvestmentLeads(response);
      setSuccess('Investment opportunities generated successfully with AI analysis!');
    } catch (err) {
      console.error('Failed to generate leads:', err);
      setError('Failed to generate investment analysis. Make sure you have extracted financial data first.');
    } finally {
      setGeneratingLeads(false);
    }
  };

  const handleSendEmail = async () => {
    if (!reportId || !emailRecipient.trim()) {
      setError('Please enter a valid email address');
      return;
    }

    try {
      setSendingEmail(true);
      setError(null);
      setSuccess(null);

      // Use the NEW investment leads email endpoint
      const emails = emailRecipient.split(',').map(e => e.trim()).filter(e => e);
      await reportService.emailInvestmentLeads(parseInt(reportId), emails, false);
      setSuccess(`Investment analysis sent successfully to ${emails.join(', ')}!`);
      setEmailRecipient('');
    } catch (err) {
      console.error('Failed to send email:', err);
      setError('Failed to send email. Please try again.');
    } finally {
      setSendingEmail(false);
    }
  };

  const getRatingColor = (rating: string) => {
    if (rating?.includes('Strong Buy') || rating?.includes('Buy')) return 'text-green-600';
    if (rating?.includes('Hold')) return 'text-yellow-600';
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

  const getRecommendationColor = (recommendation: string) => {
    const lower = recommendation.toLowerCase();
    if (lower.includes('strong buy') || lower.includes('buy')) return 'rec-buy';
    if (lower.includes('hold')) return 'rec-hold';
    if (lower.includes('sell')) return 'rec-sell';
    return 'rec-neutral';
  };

  if (loading) {
    return (
      <ReportLayout report={report || {} as Report}>
        <div className="email-page">
          <SkeletonCard />
        </div>
      </ReportLayout>
    );
  }

  if (!report) {
    return (
      <ReportLayout report={{} as Report}>
        <div className="email-page">
          <div className="email-error-state">
            <AlertCircle className="error-icon" />
            <p>Report not found</p>
          </div>
        </div>
      </ReportLayout>
    );
  }

  return (
    <ReportLayout report={report}>
      <div className="email-page">
        {/* Alert Messages */}
        {error && (
          <div className="email-alert email-alert-error">
            <AlertCircle className="alert-icon" />
            <span>{error}</span>
          </div>
        )}
        {success && (
          <div className="email-alert email-alert-success">
            <CheckCircle className="alert-icon" />
            <span>{success}</span>
          </div>
        )}

        {/* Lead Generation Section */}
        <div className="email-card">
          <div className="email-card-header">
            <Sparkles className="card-header-icon" />
            <h2 className="card-header-title">AI Investment Analysis</h2>
          </div>
          
          <p className="card-description">
            Generate comprehensive investment opportunities, risks, and growth catalysts using advanced AI analysis.
          </p>

          <button
            onClick={handleGenerateLeads}
            disabled={generatingLeads}
            className="email-action-btn btn-generate"
          >
            {generatingLeads ? (
              <>
                <Loader className="btn-icon spin" />
                <span>Analyzing with AI...</span>
              </>
            ) : (
              <>
                <Sparkles className="btn-icon" />
                <span>Generate Investment Analysis</span>
              </>
            )}
          </button>

          {/* Investment Leads Display */}
          {investmentLeads && (
            <div className="lead-analysis">
              {/* Investment Rating Card */}
              <div className="lead-score-card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                <div className="score-label" style={{ color: 'white' }}>Investment Rating</div>
                <div className={`score-value ${getRatingColor(investmentLeads.rating)}`} style={{ color: 'white', fontSize: '2rem' }}>
                  {investmentLeads.rating}
                </div>
                <div style={{ color: 'rgba(255,255,255,0.9)', marginTop: '0.5rem' }}>
                  {investmentLeads.company}
                </div>
                <div style={{ color: 'rgba(255,255,255,0.8)', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                  {investmentLeads.summary}
                </div>
              </div>

              {/* Opportunities */}
              <div className="lead-section">
                <h3 className="lead-section-title" style={{ color: '#10b981' }}>
                  <TrendingUp className="section-icon" />
                  Investment Opportunities
                </h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {investmentLeads.opportunities.map((opp, index) => (
                    <div key={index} style={{ 
                      padding: '1rem', 
                      border: '1px solid #d1fae5', 
                      borderRadius: '8px',
                      background: '#f0fdf4'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                        <strong style={{ color: '#065f46' }}>{opp.title}</strong>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <span className={`px-2 py-1 text-xs rounded ${getPotentialBadge(opp.potential)}`}>
                            {opp.potential}
                          </span>
                          <span style={{ 
                            padding: '0.25rem 0.5rem', 
                            fontSize: '0.75rem', 
                            background: '#dbeafe',
                            color: '#1e40af',
                            borderRadius: '4px'
                          }}>
                            {opp.timeframe}
                          </span>
                        </div>
                      </div>
                      <p style={{ color: '#374151', fontSize: '0.9rem' }}>{opp.evidence}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risks */}
              <div className="lead-section">
                <h3 className="lead-section-title" style={{ color: '#ef4444' }}>
                  <AlertCircle className="section-icon" />
                  Risk Factors
                </h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {investmentLeads.risks.map((risk, index) => (
                    <div key={index} style={{ 
                      padding: '1rem', 
                      border: '1px solid #fecaca', 
                      borderRadius: '8px',
                      background: '#fef2f2'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                        <strong style={{ color: '#991b1b' }}>{risk.title}</strong>
                        <span className={`px-2 py-1 text-xs rounded ${getSeverityBadge(risk.severity)}`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p style={{ color: '#374151', fontSize: '0.9rem' }}>{risk.evidence}</p>
                      {risk.mitigation && (
                        <p style={{ color: '#059669', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                          <strong>Mitigation:</strong> {risk.mitigation}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Growth Catalysts */}
              <div className="lead-section">
                <h3 className="lead-section-title" style={{ color: '#8b5cf6' }}>
                  <Sparkles className="section-icon" />
                  Growth Catalysts
                </h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {investmentLeads.catalysts.map((catalyst, index) => (
                    <div key={index} style={{ 
                      padding: '1rem', 
                      border: '1px solid #ddd6fe', 
                      borderRadius: '8px',
                      background: '#faf5ff'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                        <strong style={{ color: '#5b21b6' }}>{catalyst.title}</strong>
                        <span className={`px-2 py-1 text-xs rounded ${getImpactBadge(catalyst.impact)}`}>
                          {catalyst.impact}
                        </span>
                      </div>
                      <p style={{ color: '#374151', fontSize: '0.9rem' }}>{catalyst.evidence}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Email Section */}
        <div className="email-card">
          <div className="email-card-header">
            <Mail className="card-header-icon" />
            <h2 className="card-header-title">Email Investment Analysis</h2>
          </div>

          <p className="card-description">
            Send the AI-generated investment analysis with opportunities, risks, and catalysts to investors or analysts.
          </p>

          <div className="email-input-group">
            <input
              type="email"
              value={emailRecipient}
              onChange={(e) => setEmailRecipient(e.target.value)}
              placeholder="investor@fund.com, analyst@firm.com (comma-separated)"
              className="email-input"
              disabled={sendingEmail}
            />
            <button
              onClick={handleSendEmail}
              disabled={sendingEmail || !emailRecipient.trim() || !investmentLeads}
              className="email-action-btn btn-send"
            >
              {sendingEmail ? (
                <>
                  <Loader className="btn-icon spin" />
                  <span>Sending...</span>
                </>
              ) : (
                <>
                  <Send className="btn-icon" />
                  <span>Send Email</span>
                </>
              )}
            </button>
          </div>

          <div className="email-features">
            <p className="features-title">Email includes:</p>
            <ul className="features-list">
              <li>
                <CheckCircle className="feature-icon" />
                Investment Rating & Summary
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Investment Opportunities
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Risk Factors & Mitigations
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Growth Catalysts
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Professional HTML Format
              </li>
            </ul>
          </div>
        </div>

        {/* Department Leads Extraction Section (NEW) */}
        <div className="email-card" style={{ borderLeft: '4px solid #8b5cf6' }}>
          <div className="email-card-header">
            <Mail className="card-header-icon" />
            <h2 className="card-header-title">Department Leads Extraction</h2>
          </div>

          <p className="card-description">
            Automatically extracts department-wise leads from the Excel file generated from your report,
            analyzing growth indicators, status updates, and work progress using AI.
          </p>

          <div style={{ 
            padding: '1.25rem', 
            marginBottom: '1.5rem',
            border: '1px solid rgba(139, 92, 246, 0.2)', 
            borderRadius: '0.25rem',
            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%)'
          }}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
              <Sparkles style={{ width: '1.25rem', height: '1.25rem', marginTop: '0.125rem', color: '#a78bfa', flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <h4 style={{ marginBottom: '0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.95rem' }}>
                  Auto-Extract from Generated Excel
                </h4>
                <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem', color: '#cbd5e1', lineHeight: 1.6, listStyleType: 'disc' }}>
                  <li><strong>Growth indicators</strong> - revenue trends, expansion opportunities</li>
                  <li><strong>Status updates</strong> - current state of department work</li>
                  <li><strong>Work progress</strong> - ongoing projects and achievements</li>
                </ul>
                <div style={{ 
                  marginTop: '1rem', 
                  padding: '0.75rem',
                  background: 'rgba(139, 92, 246, 0.1)',
                  border: '1px solid rgba(139, 92, 246, 0.2)',
                  borderRadius: '0.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <Mail style={{ width: '1rem', height: '1rem', color: '#a78bfa', flexShrink: 0 }} />
                  <span style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>
                    Results emailed to: <span style={{ fontFamily: 'monospace', color: '#e2e8f0', fontWeight: 600 }}>swagatpatel03@gmail.com</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={async () => {
              if (!reportId) return;
              try {
                setLoading(true);
                setError(null);
                setSuccess(null);
                const response = await reportService.extractDepartmentLeads(parseInt(reportId), true);
                setSuccess(`✅ ${response.message}\n📧 Email sent to: swagatpatel03@gmail.com\n📊 ${response.leads.departments?.length || 0} department(s) analyzed`);
              } catch (err: any) {
                setError(`Failed to extract department leads: ${err.response?.data?.detail || err.message}`);
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading}
            className="email-action-btn btn-generate"
          >
            {loading ? (
              <>
                <Loader className="btn-icon spin" />
                <span>Analyzing with AI...</span>
              </>
            ) : (
              <>
                <Sparkles className="btn-icon" />
                <span>Extract & Email Department Leads</span>
              </>
            )}
          </button>

          <div className="email-features">
            <p className="features-title">Feature includes:</p>
            <ul className="features-list">
              <li>
                <CheckCircle className="feature-icon" />
                Auto-generated Excel analysis
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Department-wise lead extraction
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Growth & status indicators
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Powered by Groq AI
              </li>
              <li>
                <CheckCircle className="feature-icon" />
                Automatic email delivery
              </li>
            </ul>
          </div>
        </div>
      </div>
    </ReportLayout>
  );
};

export default EmailPage;
