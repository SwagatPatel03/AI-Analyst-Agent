import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import AnalysisView from '../Dashboard/AnalysisView';
import { Footer, Header } from '../Layout';
import './ReportAnalysisPage.css';

const ReportAnalysisPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      if (!reportId) {
        setError('No report ID provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const reports = await reportService.getReports();
        const foundReport = reports.reports.find((r: Report) => r.id.toString() === reportId);
        
        if (!foundReport) {
          setError('Report not found');
          setLoading(false);
          return;
        }

        if (foundReport.status !== 'completed') {
          setError('Report is not ready for analysis');
          setLoading(false);
          return;
        }

        setReport(foundReport);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch report:', err);
        setError('Failed to load report');
        setLoading(false);
      }
    };

    fetchReport();
  }, [reportId]);

  const handleBack = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className="report-analysis-page">
        <Header showUserInfo={true} />
        <main className="report-analysis-main">
          <div className="report-analysis-loading">
            <div className="loading-spinner">
              <div className="spinner-ring"></div>
              <div className="spinner-ring spinner-ring-animated"></div>
            </div>
            <p className="loading-text">Loading report analysis...</p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="report-analysis-page">
        <Header showUserInfo={true} />
        <main className="report-analysis-main">
          <div className="report-analysis-error">
            <div className="error-icon">
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="error-title">Unable to Load Report</h2>
            <p className="error-message">{error || 'Report not found'}</p>
            <button onClick={handleBack} className="error-back-btn">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Back to Dashboard</span>
            </button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="report-analysis-page">
      <Header showUserInfo={true} />
      <main className="report-analysis-main">
        <AnalysisView report={report} onBack={handleBack} />
      </main>
      <Footer />
    </div>
  );
};

export default ReportAnalysisPage;
