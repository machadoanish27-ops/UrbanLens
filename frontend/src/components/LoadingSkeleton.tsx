import React from 'react';

interface LoadingSkeletonProps {
  count?: number;
  height?: string;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  count = 1,
  height = 'h-24',
  className = '',
}) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`w-full rounded-xl bg-slate-900/80 border border-slate-800/60 animate-pulse ${height}`}
        >
          <div className="p-4 flex flex-col justify-between h-full">
            <div className="h-4 bg-slate-800 rounded w-1/3 mb-2"></div>
            <div className="h-6 bg-slate-800/60 rounded w-2/3"></div>
            <div className="h-3 bg-slate-800/40 rounded w-1/4 mt-2"></div>
          </div>
        </div>
      ))}
    </div>
  );
};
