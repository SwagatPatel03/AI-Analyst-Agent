import React from 'react';
import Skeleton from './Skeleton';
import './SkeletonCard.css';

const SkeletonCard: React.FC = () => {
  return (
    <div className="skeleton-card-wrapper">
      <div className="skeleton-card-header">
        <Skeleton width="60%" height="1.5rem" borderRadius="0.375rem" />
        <Skeleton width="80px" height="1rem" borderRadius="0.25rem" />
      </div>
      <div className="skeleton-card-body">
        <Skeleton width="100%" height="1rem" className="skeleton-card-line" />
        <Skeleton width="95%" height="1rem" className="skeleton-card-line" />
        <Skeleton width="90%" height="1rem" className="skeleton-card-line" />
        <Skeleton width="85%" height="1rem" className="skeleton-card-line" />
      </div>
      <div className="skeleton-card-footer">
        <Skeleton width="100px" height="2.5rem" borderRadius="0.5rem" />
        <Skeleton width="100px" height="2.5rem" borderRadius="0.5rem" />
      </div>
    </div>
  );
};

export default SkeletonCard;
