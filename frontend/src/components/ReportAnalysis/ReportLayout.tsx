import { ArrowLeft, BarChart3, Download, FileText, Mail, MessageSquare, Sparkles, TrendingUp } from 'lucide-react';
import React, { useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import { Footer, Header } from '../Layout';
import './ReportLayout.css';

interface ReportLayoutProps {
  children: React.ReactNode;
  report: Report;
}

const ReportLayout: React.FC<ReportLayoutProps> = ({ children, report }) => {
  const { reportId } = useParams();
  const location = useLocation();
  const [downloading, setDownloading] = useState(false);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText, path: `/report/${reportId}/overview` },
    { id: 'charts', label: 'Charts', icon: BarChart3, path: `/report/${reportId}/charts` },
    { id: 'predictions', label: 'Predictions', icon: TrendingUp, path: `/report/${reportId}/predictions` },
    { id: 'chat', label: 'Chatbot', icon: MessageSquare, path: `/report/${reportId}/chat` },
    { id: 'agent', label: 'AI Agent', icon: Sparkles, path: `/report/${reportId}/agent` },
    { id: 'email', label: 'Email & Leads', icon: Mail, path: `/report/${reportId}/email` }
  ];

  const isActiveTab = (path: string) => location.pathname === path;

  const handleDownloadExcel = async () => {
    if (!report?.id) return;
    
    try {
      setDownloading(true);
      const blob = await reportService.downloadExcel(report.id);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${report.company_name}_financial_data.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download Excel:', err);
      alert('Failed to download Excel file. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="report-layout">
      <Header showUserInfo={true} />
      
      <main className="report-layout-main">
        {/* Report Header */}
        <div className="report-header">
          <div className="report-header-content">
            <Link to="/dashboard" className="report-back-btn">
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Dashboard</span>
            </Link>
            
            <div className="report-title-section">
              <div className="report-title-wrapper">
                <FileText className="report-title-icon" />
                <div>
                  <h1 className="report-title">{report.company_name}</h1>
                  <div className="report-meta">
                    <span className="report-meta-item">Year: {report.report_year || 'N/A'}</span>
                    <span className="report-meta-divider">•</span>
                    <span className="report-meta-item">Uploaded: {new Date(report.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}</span>
                  </div>
                </div>
              </div>
              
              <button
                onClick={handleDownloadExcel}
                disabled={downloading}
                className="report-download-btn"
              >
                <Download className="w-5 h-5" />
                <span>{downloading ? 'Downloading...' : 'Download Excel'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="report-tabs-container">
          <div className="report-tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const active = isActiveTab(tab.path);
              return (
                <Link
                  key={tab.id}
                  to={tab.path}
                  className={`report-tab ${active ? 'active' : ''}`}
                >
                  <Icon className="report-tab-icon" />
                  <span>{tab.label}</span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Page Content */}
        <div className="report-content">
          {children}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default ReportLayout;
