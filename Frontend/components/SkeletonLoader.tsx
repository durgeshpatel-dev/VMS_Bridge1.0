import React from 'react';

interface SkeletonLoaderProps {
  variant?: 'card' | 'table' | 'list' | 'metric' | 'detail' | 'chart';
  count?: number;
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  variant = 'card', 
  count = 1,
  className = '' 
}) => {
  const renderSkeleton = () => {
    switch (variant) {
      case 'metric':
        return (
          <div className={`flex flex-col gap-2 rounded-xl p-5 border border-border bg-surface shadow-sm animate-pulse ${className}`}>
            <div className="flex justify-between items-start">
              <div className="h-4 bg-border rounded w-24"></div>
              <div className="h-6 w-6 bg-border rounded"></div>
            </div>
            <div className="h-8 bg-border rounded w-16 mt-1"></div>
          </div>
        );

      case 'card':
        return (
          <div className={`bg-surface border border-border rounded-lg p-4 animate-pulse ${className}`}>
            <div className="flex items-center justify-between mb-3">
              <div className="h-5 bg-border rounded w-32"></div>
              <div className="h-4 w-4 bg-border rounded-full"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 bg-border rounded w-full"></div>
              <div className="h-4 bg-border rounded w-3/4"></div>
            </div>
            <div className="flex gap-2 mt-4">
              <div className="h-6 bg-border rounded-full w-16"></div>
              <div className="h-6 bg-border rounded-full w-20"></div>
            </div>
          </div>
        );

      case 'table':
        return (
          <div className={`bg-surface border-b border-border p-4 animate-pulse ${className}`}>
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 bg-border rounded"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-border rounded w-48"></div>
                <div className="h-3 bg-border rounded w-32"></div>
              </div>
              <div className="h-8 bg-border rounded w-24"></div>
            </div>
          </div>
        );

      case 'list':
        return (
          <div className={`bg-surface border-b border-border p-3 animate-pulse ${className}`}>
            <div className="flex items-start gap-3">
              <div className="h-2 w-2 bg-border rounded-full mt-1.5"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-border rounded w-full"></div>
                <div className="h-3 bg-border rounded w-2/3"></div>
                <div className="flex gap-2 mt-2">
                  <div className="h-5 bg-border rounded-full w-16"></div>
                  <div className="h-5 bg-border rounded-full w-20"></div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'detail':
        return (
          <div className={`bg-surface border border-border rounded-lg p-6 animate-pulse ${className}`}>
            <div className="space-y-4">
              <div className="h-6 bg-border rounded w-3/4"></div>
              <div className="flex gap-2">
                <div className="h-7 bg-border rounded-full w-24"></div>
                <div className="h-7 bg-border rounded-full w-20"></div>
                <div className="h-7 bg-border rounded-full w-28"></div>
              </div>
              <div className="space-y-2 pt-4 border-t border-border">
                <div className="h-4 bg-border rounded w-full"></div>
                <div className="h-4 bg-border rounded w-full"></div>
                <div className="h-4 bg-border rounded w-5/6"></div>
              </div>
            </div>
          </div>
        );

      case 'chart':
        return (
          <div className={`bg-surface border border-border rounded-lg p-6 animate-pulse ${className}`}>
            <div className="h-5 bg-border rounded w-32 mb-4"></div>
            <div className="h-64 bg-border rounded"></div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <React.Fragment key={i}>
          {renderSkeleton()}
        </React.Fragment>
      ))}
    </>
  );
};

// Specialized skeleton components for common use cases
export const MetricsSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <SkeletonLoader variant="metric" count={4} />
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="space-y-0">
    <SkeletonLoader variant="table" count={rows} />
  </div>
);

export const ListSkeleton: React.FC<{ items?: number }> = ({ items = 5 }) => (
  <div className="space-y-0">
    <SkeletonLoader variant="list" count={items} />
  </div>
);

export const DetailSkeleton: React.FC = () => (
  <div className="space-y-6">
    <SkeletonLoader variant="detail" />
    <SkeletonLoader variant="detail" />
  </div>
);
