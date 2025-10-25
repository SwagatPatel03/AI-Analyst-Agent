import { BarChart3, Info, Sparkles, TrendingUp } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { reportService } from '../../services/reportService';
import type { Predictions, Report } from '../../types';
import { getErrorMessage } from '../../utils/helpers';
import { SkeletonCard, SkeletonChart } from '../Skeleton';
import './PredictionsPage.css';
import ReportLayout from './ReportLayout';

const PredictionsPage: React.FC = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState<Report | null>(null);
  const [predictions, setPredictions] = useState<Predictions | null>(null);
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
        return;
      }

      setReport(foundReport);
      await loadPredictions();
    } catch (err) {
      console.error('Failed to fetch report:', err);
      setError('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  const loadPredictions = async () => {
    if (!reportId) return;

    try {
      const data = await reportService.getPredictions(parseInt(reportId));
      setPredictions(data.predictions);
    } catch (err) {
      console.error('Failed to load predictions:', err);
      // Don't show error for empty predictions
    }
  };

  const generatePredictions = async () => {
    if (!reportId) return;

    try {
      setGenerating(true);
      setError('');
      setSuccess('');
      
      const data = await reportService.generatePredictions(parseInt(reportId));
      setPredictions(data.predictions);
      
      setSuccess('Predictions generated successfully!');
    } catch (err) {
      const message = getErrorMessage(err);
      setError(`Failed to generate predictions: ${message}`);
    } finally {
      setGenerating(false);
    }
  };

  if (loading || !report) {
    return (
      <div className="predictions-page">
        <SkeletonCard />
        <div style={{ marginTop: '2rem' }}>
          <SkeletonChart height="350px" showLegend={true} />
        </div>
        <div style={{ marginTop: '2rem' }}>
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <ReportLayout report={report}>
      <div className="predictions-page">
        {/* Alert Messages */}
        {error && (
          <div className="predictions-alert predictions-alert-error">
            {error}
          </div>
        )}
        {success && (
          <div className="predictions-alert predictions-alert-success">
            {success}
          </div>
        )}

        {/* Main Content */}
        {generating ? (
          <div className="predictions-empty-state">
            <div className="loading-spinner-large">
              <div className="spinner-ring-large"></div>
              <div className="spinner-ring-large spinner-animated"></div>
            </div>
            <p className="predictions-empty-title">Generating predictions...</p>
            <p className="predictions-empty-text">Analyzing financial data with ML models</p>
          </div>
        ) : predictions && predictions.growth_rate ? (
          <>
            {/* Growth Prediction Card */}
            <div className="predictions-growth-card">
              <h3 className="predictions-card-title">
                <TrendingUp className="predictions-card-icon" />
                Growth Prediction
              </h3>
              <div className="predictions-growth-main">
                <div className="predictions-growth-value">
                  {predictions.growth_rate.predicted}%
                </div>
                <div className="predictions-growth-label">Predicted Growth Rate</div>
              </div>
              <div className="predictions-confidence-grid">
                <div className="predictions-confidence-item">
                  <div className="predictions-confidence-label">Lower Bound</div>
                  <div className="predictions-confidence-value">{predictions.growth_rate.confidence_lower}%</div>
                </div>
                <div className="predictions-confidence-item">
                  <div className="predictions-confidence-label">Confidence Level</div>
                  <div className="predictions-confidence-value">{(predictions.growth_rate.confidence_level * 100).toFixed(0)}%</div>
                </div>
                <div className="predictions-confidence-item">
                  <div className="predictions-confidence-label">Upper Bound</div>
                  <div className="predictions-confidence-value">{predictions.growth_rate.confidence_upper}%</div>
                </div>
              </div>
            </div>

            {/* Sales Forecast Card */}
            {predictions.sales_forecast && predictions.sales_forecast.length > 0 && (
              <div className="predictions-card">
                <h3 className="predictions-card-title">
                  <BarChart3 className="predictions-card-icon predictions-icon-green" />
                  Sales Forecast (Next 3 Years)
                </h3>
                <div className="predictions-forecast-list">
                  {predictions.sales_forecast.map((forecast, idx) => (
                    <div key={idx} className="predictions-forecast-item">
                      <div className="predictions-forecast-info">
                        <div className="predictions-forecast-year">Year {forecast.year}</div>
                        <div className="predictions-forecast-growth">Growth: {forecast.growth_rate}%</div>
                      </div>
                      <div className="predictions-forecast-revenue">
                        {forecast.predicted_revenue.toLocaleString()} {forecast.currency}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Segment Breakdown Card */}
            {predictions.segment_breakdown && predictions.segment_breakdown.length > 0 && (
              <div className="predictions-card">
                <h3 className="predictions-card-title">
                  <Sparkles className="predictions-card-icon predictions-icon-purple" />
                  Segment Breakdown
                </h3>
                <div className="predictions-segment-list">
                  {predictions.segment_breakdown.map((segment, idx) => (
                    <div key={idx} className="predictions-segment-item">
                      <div className="predictions-segment-info">
                        <div className="predictions-segment-name">{segment.segment}</div>
                        <div className="predictions-segment-details">
                          Current: {segment.current_revenue.toLocaleString()} ({segment.proportion}%)
                        </div>
                      </div>
                      <div className="predictions-segment-growth">
                        <div className={`predictions-segment-value ${segment.predicted_growth >= 0 ? 'positive' : 'negative'}`}>
                          {segment.predicted_growth >= 0 ? '+' : ''}{segment.predicted_growth}%
                        </div>
                        <div className="predictions-segment-label">Predicted Growth</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations Card */}
            {predictions.recommendations && predictions.recommendations.length > 0 && (
              <div className="predictions-card">
                <h3 className="predictions-card-title">
                  <Info className="predictions-card-icon predictions-icon-blue" />
                  Investment Recommendations
                </h3>
                <div className="predictions-recommendations-list">
                  {predictions.recommendations.map((rec, idx) => (
                    <div key={idx} className="predictions-recommendation-item">
                      <span className="predictions-recommendation-number">{idx + 1}</span>
                      <span className="predictions-recommendation-text">
                        {typeof rec === 'string' ? rec : rec.description}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : predictions && predictions.success === false ? (
          /* Insufficient Data State */
          <div className="predictions-error-state">
            <div className="predictions-error-icon">⚠️</div>
            <h3 className="predictions-error-title">
              {predictions.error || 'Unable to Generate Predictions'}
            </h3>
            
            {predictions.recommendations && predictions.recommendations.length > 0 && (
              <div className="predictions-error-recommendations">
                <h4 className="predictions-error-rec-title">Recommendations:</h4>
                <div className="predictions-error-rec-list">
                  {predictions.recommendations.map((rec, idx) => (
                    <div key={idx} className="predictions-error-rec-item">
                      {typeof rec === 'string' ? (
                        <p className="predictions-error-rec-text">{rec}</p>
                      ) : (
                        <div className="predictions-error-rec-content">
                          {rec.icon && <span className="predictions-error-rec-icon">{rec.icon}</span>}
                          <div className="predictions-error-rec-body">
                            {rec.title && (
                              <h5 className="predictions-error-rec-heading">{rec.title}</h5>
                            )}
                            {rec.description && (
                              <p className="predictions-error-rec-desc">{rec.description}</p>
                            )}
                            {rec.action && (
                              <p className="predictions-error-rec-action">{rec.action}</p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="predictions-tip">
              💡 <strong>Tip:</strong> Make sure your Excel file contains complete financial statements including revenue, expenses, balance sheet data, and key financial ratios for accurate ML predictions.
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className="predictions-empty-state">
            <TrendingUp className="predictions-empty-icon" />
            <p className="predictions-empty-title">No predictions generated yet</p>
            <p className="predictions-empty-text">
              Click the button below to generate ML-powered growth predictions and sales forecasts
            </p>
            <button
              onClick={generatePredictions}
              disabled={generating}
              className="predictions-generate-btn"
            >
              <TrendingUp className="w-6 h-6" />
              <span>Generate Predictions</span>
            </button>
          </div>
        )}
      </div>
    </ReportLayout>
  );
};

export default PredictionsPage;
