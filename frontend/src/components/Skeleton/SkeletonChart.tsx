import React from 'react';
import Skeleton from './Skeleton';
import './SkeletonChart.css';

interface SkeletonChartProps {
  height?: string;
  showLegend?: boolean;
}

const SkeletonChart: React.FC<SkeletonChartProps> = ({ 
  height = '300px',
  showLegend = true 
}) => {
  return (
    <div className="skeleton-chart-wrapper">
      {/* Chart Header */}
      <div className="skeleton-chart-header">
        <Skeleton width="40%" height="1.5rem" />
        <Skeleton width="80px" height="2rem" borderRadius="0.5rem" />
      </div>

      {/* Chart Area */}
      <div className="skeleton-chart-area" style={{ height }}>
        <Skeleton width="100%" height="100%" borderRadius="0.5rem" />
      </div>

      {/* Legend (Optional) */}
      {showLegend && (
        <div className="skeleton-chart-legend">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton-legend-item">
              <Skeleton width="12px" height="12px" borderRadius="50%" />
              <Skeleton width="60px" height="1rem" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SkeletonChart;
