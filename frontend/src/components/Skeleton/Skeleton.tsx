import React from 'react';
import './Skeleton.css';

interface SkeletonProps {
  width?: string;
  height?: string;
  borderRadius?: string;
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({ 
  width = '100%', 
  height = '1rem', 
  borderRadius = '0.25rem',
  className = ''
}) => {
  return (
    <div 
      className={`skeleton ${className}`}
      style={{ width, height, borderRadius }}
    />
  );
};

export default Skeleton;
