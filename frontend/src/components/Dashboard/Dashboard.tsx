import {
    AlertCircle,
    Calendar,
    FileText,
    RefreshCw,
    Search,
    TrendingUp,
    Upload
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import AnimatedBackground from '../Background/AnimatedBackground';
import { Footer, Header } from '../Layout';
import FileUpload from '../Upload/FileUpload';
import './Dashboard.css';
import './ReportCard.css';
import './UploadModal.css';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<Report[]>([]);
  const [filteredReports, setFilteredReports] = useState<Report[]>([]);
  const [showUpload, setShowUpload] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadReports();
  }, []);

  useEffect(() => {
    // Filter reports based on search query
    if (searchQuery.trim() === '') {
      setFilteredReports(reports);
    } else {
      const filtered = reports.filter(report =>
        report.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        report.report_year?.toString().includes(searchQuery)
      );
      setFilteredReports(filtered);
    }
  }, [searchQuery, reports]);

  const loadReports = async () => {
    try {
      setLoading(true);
      const data = await reportService.getReports();
      setReports(data.reports);
      setFilteredReports(data.reports);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadComplete = () => {
    setShowUpload(false);
    loadReports();
  };

  const handleReportSelect = (report: Report) => {
    if (report.status === 'completed') {
      navigate(`/report/${report.id}/overview`);
    }
  };

  return (
    <div className="dashboard-container">
      <AnimatedBackground />
      <Header showUserInfo={true} />

      <main className="dashboard-main">
        <div className="dashboard-content">
          {/* Action Bar */}
          <div className="dashboard-action-bar">
            <div className="dashboard-button-group">
              <button
                onClick={() => setShowUpload(true)}
                className="dashboard-upload-btn"
              >
                <Upload className="w-5 h-5" />
                <span>Upload Report</span>
              </button>
              
              <button
                onClick={loadReports}
                className="dashboard-refresh-btn"
                aria-label="Refresh reports"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="dashboard-search-container">
              <div className="dashboard-search-icon">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="dashboard-search-input"
                placeholder="Search by company or year..."
              />
            </div>
          </div>

        {/* Upload Modal */}
        {showUpload && (
          <div className="upload-modal-overlay">
            <div className="upload-modal">
              <div className="upload-modal-header">
                <h2 className="upload-modal-title">
                  <Upload />
                  Upload Annual Report
                </h2>
                <button
                  onClick={() => setShowUpload(false)}
                  className="upload-modal-close"
                  aria-label="Close modal"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="upload-modal-body">
                <FileUpload onUploadComplete={handleUploadComplete} />
              </div>
            </div>
          </div>
        )}

        {/* Reports Grid */}
        {loading ? (
          <div className="dashboard-loading">
            <div className="dashboard-spinner-container">
              <div className="dashboard-spinner-track"></div>
              <div className="dashboard-spinner"></div>
            </div>
            <p className="dashboard-loading-text">Loading reports...</p>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="dashboard-empty-state">
            <div className="dashboard-empty-icon-wrapper">
              <div className="dashboard-empty-icon">
                <FileText />
              </div>
            </div>
            <h3 className="dashboard-empty-title">
              {searchQuery ? 'No reports found' : 'No reports yet'}
            </h3>
            <p className="dashboard-empty-description">
              {searchQuery 
                ? 'Try adjusting your search criteria' 
                : 'Upload your first annual report to get started with AI-powered analysis'}
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowUpload(true)}
                className="dashboard-empty-upload-btn"
              >
                <Upload />
                <span>Upload Report</span>
              </button>
            )}
          </div>
        ) : (
          <>
            {/* Reports Section Header */}
            <div className="dashboard-reports-header">
              <div className="dashboard-section-title">
                <h2 className="dashboard-title-text">Your Reports</h2>
                <p className="dashboard-title-description">
                  Manage and analyze your annual reports with AI-powered insights
                </p>
              </div>
              <div className="dashboard-report-count">
                <span>Showing</span>
                <span className="count-highlight">{filteredReports.length}</span>
                <span>of</span>
                <span className="count-highlight">{reports.length}</span>
                <span>reports</span>
              </div>
            </div>

            {/* Reports Grid */}
            <div className="report-cards-grid">
              {filteredReports.map((report) => (
                <div
                  key={report.id}
                  onClick={() => handleReportSelect(report)}
                  className={`report-card ${
                    report.status !== 'completed' ? 'disabled' : ''
                  }`}
                >
                  {/* Card Header */}
                  <div className="report-card-header">
                    <div className="report-card-icon">
                      <FileText className="w-8 h-8 text-indigo-600" />
                    </div>
                    <span className={`report-card-status status-${report.status}`}>
                      {report.status}
                    </span>
                  </div>
                  
                  {/* Company Name */}
                  <h3 className="report-card-company">
                    {report.company_name}
                  </h3>
                  
                  {/* Card Divider */}
                  <div className="report-card-divider"></div>
                  
                  {/* Meta Information */}
                  <div className="report-card-meta">
                    <div className="report-card-meta-item">
                      <span className="report-card-meta-label">Year:</span>
                      <span className="report-card-year">{report.report_year || 'N/A'}</span>
                    </div>
                    <div className="report-card-meta-item">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="report-card-date">
                        {new Date(report.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </span>
                    </div>
                    <div className="report-card-meta-item">
                      <span className="report-card-filename">
                        <FileText className="w-3.5 h-3.5" />
                        <span className="report-card-filename-text">{report.filename}</span>
                      </span>
                    </div>
                  </div>

                  {/* Card Footer */}
                  {report.status === 'completed' && (
                    <div className="report-card-footer">
                      <div className="report-card-action">
                        <TrendingUp className="w-5 h-5" />
                        <span>Click to analyze</span>
                      </div>
                    </div>
                  )}

                  {report.status === 'processing' && (
                    <div className="report-card-footer">
                      <div className="report-card-processing">
                        <div className="report-card-spinner"></div>
                        <span>Processing document...</span>
                      </div>
                    </div>
                  )}

                  {report.status === 'failed' && (
                    <div className="report-card-footer">
                      <div className="report-card-failed">
                        <AlertCircle className="w-5 h-5" />
                        <span>Processing failed</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Dashboard;
