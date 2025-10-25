import React from 'react';
import Skeleton from './Skeleton';
import './SkeletonTable.css';

interface SkeletonTableProps {
  rows?: number;
  columns?: number;
}

const SkeletonTable: React.FC<SkeletonTableProps> = ({ rows = 5, columns = 4 }) => {
  return (
    <div className="skeleton-table">
      {/* Table Header */}
      <div className="skeleton-table-header">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton 
            key={`header-${index}`} 
            width="100%" 
            height="2rem" 
            borderRadius="0.375rem"
          />
        ))}
      </div>

      {/* Table Rows */}
      <div className="skeleton-table-body">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={`row-${rowIndex}`} className="skeleton-table-row">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton 
                key={`cell-${rowIndex}-${colIndex}`} 
                width="90%" 
                height="1.25rem" 
                borderRadius="0.25rem"
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SkeletonTable;
