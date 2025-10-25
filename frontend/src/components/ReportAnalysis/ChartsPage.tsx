import { BarChart3, ExternalLink, Info, Sparkles } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Report } from '../../types';
import { getErrorMessage } from '../../utils/helpers';
import CustomVisualizationBuilder from '../Dashboard/CustomVisualizationBuilder';
import { SkeletonChart } from '../Skeleton';
import './ChartsPage.css';
import ReportLayout from './ReportLayout';

const ChartsPage: React.FC = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState<Report | null>(null);
  const [visualizations, setVisualizations] = useState<string[]>([]);
  const [customVisualizations, setCustomVisualizations] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showCustomBuilder, setShowCustomBuilder] = useState(false);
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
        return;
      }

      setReport(foundReport);
      await loadVisualizations();
      await loadCustomVisualizations();
    } catch (err) {
      console.error('Failed to fetch report:', err);
      setError('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const loadVisualizations = async () => {
    if (!reportId) return;

    try {
      const data = await reportService.getVisualizations(parseInt(reportId));
      
      // Convert to array - handle both array and object formats
      let vizArray: string[] = [];
      if (Array.isArray(data.visualizations)) {
        vizArray = data.visualizations;
      } else if (data.visualizations && typeof data.visualizations === 'object') {
        vizArray = Object.values(data.visualizations);
      }
      
      setVisualizations(vizArray);
    } catch (err) {
      console.error('Failed to load visualizations:', err);
      // Don't show error for empty visualizations
    }
  };

  const loadCustomVisualizations = async () => {
    if (!reportId) return;

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${API_BASE_URL}/analysis/custom-visualizations/${reportId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setCustomVisualizations(data.custom_visualizations || []);
      }
    } catch (err) {
      console.error('Failed to load custom visualizations:', err);
    }
  };

  const generateVisualizations = async () => {
    if (!reportId) return;

    try {
      setGenerating(true);
      setError('');
      setSuccess('');
      
      await reportService.generateVisualizations(parseInt(reportId));
      await loadVisualizations();
      
      setSuccess('Visualizations generated successfully!');
    } catch (err) {
      const message = getErrorMessage(err);
      setError(`Failed to generate visualizations: ${message}`);
    } finally {
      setGenerating(false);
    }
  };

  if (loading || !report) {
    return (
      <div className="charts-page">
        <div className="charts-grid">
          <SkeletonChart height="400px" showLegend={true} />
          <SkeletonChart height="400px" showLegend={true} />
          <SkeletonChart height="400px" showLegend={false} />
          <SkeletonChart height="400px" showLegend={false} />
        </div>
      </div>
    );
  }

  return (
    <ReportLayout report={report}>
      <div className="charts-page">
        {/* Alert Messages */}
        {error && (
          <div className="charts-alert charts-alert-error">
            {error}
          </div>
        )}
        {success && (
          <div className="charts-alert charts-alert-success">
            {success}
          </div>
        )}

        {/* Empty State or Charts Grid */}
        {generating ? (
          <div className="charts-empty-state">
            <div className="loading-spinner-large">
              <div className="spinner-ring-large"></div>
              <div className="spinner-ring-large spinner-animated"></div>
            </div>
            <p className="charts-empty-title">Generating visualizations...</p>
            <p className="charts-empty-text">This may take a few moments</p>
          </div>
        ) : visualizations.length === 0 && customVisualizations.length === 0 ? (
          <div className="charts-empty-state">
            <BarChart3 className="charts-empty-icon" />
            <p className="charts-empty-title">No visualizations available</p>
            <p className="charts-empty-text">
              Click the button below to generate interactive charts from your financial data
            </p>
            <button
              onClick={generateVisualizations}
              disabled={generating}
              className="charts-generate-btn"
            >
              <Sparkles className="w-6 h-6" />
              <span>Generate Visualizations</span>
            </button>
          </div>
        ) : (
          <>
            {/* Info Banner */}
            <div className="charts-info-banner">
              <div className="charts-info-content">
                <Info className="charts-info-icon" />
                <p className="charts-info-text">
                  Interactive charts generated from your financial data. Hover over elements for detailed information.
                </p>
              </div>
              <button
                onClick={generateVisualizations}
                disabled={generating}
                className="charts-regenerate-btn"
              >
                🔄 Regenerate
              </button>
            </div>

            {/* Custom Visualization Builder */}
            <div className="custom-builder-card">
              <button
                onClick={() => setShowCustomBuilder(!showCustomBuilder)}
                className="custom-builder-toggle"
              >
                <span className="custom-builder-toggle-label">
                  <Sparkles className="w-5 h-5" />
                  Create Custom Visualization
                </span>
                <span className="custom-builder-toggle-badge">
                  {showCustomBuilder ? '▼ Hide' : '▶ Show'}
                </span>
              </button>
              
              {showCustomBuilder && (
                <div className="custom-builder-content">
                  <CustomVisualizationBuilder 
                    reportId={report.id}
                    onChartCreated={() => {
                      loadCustomVisualizations();
                      setSuccess('Custom chart created! 🎉');
                      setShowCustomBuilder(false);
                    }}
                  />
                </div>
              )}
            </div>

            {/* Custom Visualizations Section */}
            {customVisualizations.length > 0 && (
              <div className="charts-section">
                <h2 className="charts-section-title">
                  <Sparkles className="charts-section-icon charts-section-icon-purple" />
                  Your Custom Charts ({customVisualizations.length})
                </h2>
                <div className="charts-grid">
                  {customVisualizations.map((viz, idx) => {
                    const cleanPath = viz
                      .replace(/\\/g, '/')
                      .replace(/^outputs\//, '');
                    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                    const fullUrl = `${apiBaseUrl}/static/${cleanPath}`;
                    
                    return (
                      <div key={idx} className="chart-card chart-card-custom">
                        <div className="chart-card-header chart-card-header-custom">
                          <h3 className="chart-card-title">
                            <span className="chart-star">⭐</span>
                            Custom Chart {idx + 1}
                          </h3>
                          <a
                            href={fullUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-card-link chart-card-link-custom"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Open
                          </a>
                        </div>
                        <iframe
                          src={fullUrl}
                          className="chart-iframe"
                          title={`Custom Chart ${idx + 1}`}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Predefined Visualizations Section */}
            {visualizations.length > 0 && (
              <div className="charts-section">
                <h2 className="charts-section-title">
                  <BarChart3 className="charts-section-icon charts-section-icon-blue" />
                  Predefined Charts ({visualizations.length})
                </h2>
                <div className="charts-grid">
                  {visualizations.map((viz, idx) => {
                    const cleanPath = viz
                      .replace(/\\/g, '/')
                      .replace(/^outputs\//, '');
                    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
                    const fullUrl = `${apiBaseUrl}/static/${cleanPath}`;
                    
                    return (
                      <div key={idx} className="chart-card">
                        <div className="chart-card-header">
                          <h3 className="chart-card-title">
                            Visualization {idx + 1}
                          </h3>
                          <a
                            href={fullUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="chart-card-link"
                          >
                            <ExternalLink className="w-4 h-4" />
                            Open
                          </a>
                        </div>
                        <iframe
                          src={fullUrl}
                          className="chart-iframe"
                          title={`Visualization ${idx + 1}`}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </ReportLayout>
  );
};

export default ChartsPage;
