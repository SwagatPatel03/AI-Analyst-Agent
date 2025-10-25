import React from 'react';
import Skeleton from './Skeleton';
import './SkeletonStats.css';

interface SkeletonStatsProps {
  count?: number;
}

const SkeletonStats: React.FC<SkeletonStatsProps> = ({ count = 4 }) => {
  return (
    <div className="skeleton-stats-grid">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="skeleton-stat-card">
          {/* Icon */}
          <div className="skeleton-stat-icon">
            <Skeleton width="48px" height="48px" borderRadius="0.75rem" />
          </div>

          {/* Content */}
          <div className="skeleton-stat-content">
            <Skeleton width="60%" height="0.875rem" />
            <Skeleton width="80%" height="2rem" />
            <Skeleton width="50%" height="0.875rem" />
          </div>
        </div>
      ))}
    </div>
  );
};

export default SkeletonStats;
