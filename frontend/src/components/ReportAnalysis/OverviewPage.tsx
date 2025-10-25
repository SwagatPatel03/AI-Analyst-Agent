import { BarChart3, Download, FileText, MessageSquare, Sparkles, TrendingUp } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import { getErrorMessage } from '../../utils/helpers';
import { SkeletonCard, SkeletonStats } from '../Skeleton';
import './OverviewPage.css';
import ReportLayout from './ReportLayout';

const OverviewPage: React.FC = () => {
  const { reportId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState<Report | null>(null);
  const [reportSummary, setReportSummary] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchReport();
  }, [reportId]);

  const fetchReport = async () => {
    if (!reportId) return;

    try {
      setLoading(true);
      const reports = await reportService.getReports();
      const foundReport = reports.reports.find((r: Report) => r.id.toString() === reportId);
      
      if (!foundReport) {
        navigate('/dashboard');
        return;
      }

      setReport(foundReport);
      
      // Check if summary already exists by trying to generate
      // If it already exists, the backend will return it
      setReportSummary('exists'); // Assume it exists, we'll check when user tries to download
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch report:', err);
      navigate('/dashboard');
    }
  };

  const handleGenerateReport = async () => {
    if (!report) return;

    try {
      setGenerating(true);
      setError('');
      setSuccess('');
      
      await reportService.generateReport(report.id);
      setReportSummary('exists');
      setSuccess('Executive summary generated successfully!');
    } catch (err) {
      const message = getErrorMessage(err);
      setError(`Failed to generate report: ${message}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!report) return;

    try {
      setGenerating(true);
      setError('');
      
      const blob = await reportService.downloadReportPDF(report.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${report.company_name}_Executive_Summary.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setSuccess('Report downloaded successfully!');
    } catch (err) {
      const message = getErrorMessage(err);
      setError(`Failed to download report: ${message}`);
    } finally {
      setGenerating(false);
    }
  };

  if (loading || !report) {
    return (
      <div className="overview-page">
        <SkeletonStats count={4} />
        <div style={{ marginTop: '2rem' }}>
          <SkeletonCard />
        </div>
        <div style={{ marginTop: '2rem' }}>
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <ReportLayout report={report}>
      <div className="overview-page">
        {/* Alert Messages */}
        {error && (
          <div className="overview-alert overview-alert-error">
            {error}
          </div>
        )}
        {success && (
          <div className="overview-alert overview-alert-success">
            {success}
          </div>
        )}

        {/* Report Overview Card */}
        <div className="overview-card">
          <h2 className="overview-card-title">
            <FileText className="overview-card-icon" />
            Report Overview
          </h2>
          <div className="overview-stats-grid">
            <div className="overview-stat overview-stat-blue">
              <p className="overview-stat-label">Company</p>
              <p className="overview-stat-value">{report.company_name}</p>
            </div>
            <div className="overview-stat overview-stat-purple">
              <p className="overview-stat-label">Report Year</p>
              <p className="overview-stat-value">{report.report_year || 'N/A'}</p>
            </div>
            <div className="overview-stat overview-stat-green">
              <p className="overview-stat-label">Status</p>
              <p className="overview-stat-value">{report.status}</p>
            </div>
            <div className="overview-stat overview-stat-orange">
              <p className="overview-stat-label">Uploaded</p>
              <p className="overview-stat-value">
                {new Date(report.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Executive Summary Card */}
        <div className="overview-card">
          <div className="overview-summary-header">
            <h3 className="overview-summary-title">
              <Sparkles className="overview-summary-icon" />
              AI-Generated Executive Summary
            </h3>
            <span className="overview-badge">Powered by Gemini AI</span>
          </div>

          {reportSummary ? (
            <div className="overview-summary-ready">
              <FileText className="overview-summary-ready-icon" />
              <p className="overview-summary-ready-title">Executive Summary Report Ready</p>
              <p className="overview-summary-ready-text">
                Download the full comprehensive report with detailed financial analysis
              </p>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button
                  onClick={handleDownloadPDF}
                  disabled={generating}
                  className="overview-download-btn"
                >
                  <Download className="w-5 h-5" />
                  <span>Download Report (PDF)</span>
                </button>
                <button
                  onClick={handleGenerateReport}
                  disabled={generating}
                  className="overview-regenerate-btn"
                  title="Regenerate the executive summary with fresh AI analysis"
                >
                  {generating ? (
                    <>
                      <div className="spinner-small"></div>
                      <span>Regenerating...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      <span>Regenerate Report</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ) : (
            <div className="overview-summary-empty">
              <FileText className="overview-summary-empty-icon" />
              <p className="overview-summary-empty-title">No Executive Summary Available</p>
              <p className="overview-summary-empty-text">
                Generate a concise AI summary to skip reading the full report
              </p>
              <button
                onClick={handleGenerateReport}
                disabled={generating}
                className="overview-generate-btn"
              >
                {generating ? (
                  <>
                    <div className="spinner-small"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Executive Summary</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Quick Actions Card */}
        <div className="overview-card">
          <h3 className="overview-actions-title">Quick Actions</h3>
          <div className="overview-actions-grid">
            <button
              onClick={() => navigate(`/report/${reportId}/charts`)}
              className="overview-action-btn overview-action-primary"
            >
              <BarChart3 className="overview-action-icon" />
              <span>View Charts</span>
            </button>
            <button
              onClick={() => navigate(`/report/${reportId}/predictions`)}
              className="overview-action-btn overview-action-green"
            >
              <TrendingUp className="overview-action-icon" />
              <span>Get Predictions</span>
            </button>
            <button
              onClick={() => navigate(`/report/${reportId}/chat`)}
              className="overview-action-btn overview-action-blue"
            >
              <MessageSquare className="overview-action-icon" />
              <span>Ask Questions</span>
            </button>
          </div>
        </div>
      </div>
    </ReportLayout>
  );
};

export default OverviewPage;
