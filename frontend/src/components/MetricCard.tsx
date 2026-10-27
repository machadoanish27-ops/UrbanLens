import React from 'react';
import { StatusBadge, type StatusType } from './StatusBadge';

interface MetricCardProps {
  label: string;
  value: string | number | null | undefined;
  unit?: string;
  subValue?: string;
  icon?: React.ReactNode;
  status?: StatusType;
  unavailableText?: string;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subValue,
  icon,
  status,
  unavailableText = 'Not Available',
  className = '',
}) => {
  const isAvailable = value !== null && value !== undefined && value !== '';

  return (
    <div
      className={`glass-panel p-4 rounded-xl flex flex-col justify-between transition-all duration-200 border border-slate-800/80 hover:border-slate-700/80 ${className}`}
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
          {label}
        </span>
        <div className="flex items-center gap-1.5">
          {status && <StatusBadge status={status} />}
          {icon && <div className="text-indigo-400">{icon}</div>}
        </div>
      </div>

      <div className="my-1">
        {isAvailable ? (
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-bold tracking-tight text-white">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </span>
            {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
          </div>
        ) : (
          <span className="text-sm font-medium text-slate-500 italic">
            {unavailableText}
          </span>
        )}
      </div>

      {subValue && (
        <p className="text-xs text-slate-400 mt-1 truncate" title={subValue}>
          {subValue}
        </p>
      )}
    </div>
  );
};
