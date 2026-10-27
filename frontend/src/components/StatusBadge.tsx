import React from 'react';
import { Clock, Database, AlertTriangle, XCircle, Sparkles } from 'lucide-react';

export type StatusType = 'fresh' | 'cached' | 'database' | 'unavailable' | 'error' | string;

interface StatusBadgeProps {
  status?: StatusType | null;
  label?: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status = 'database', label, className = '' }) => {
  const normStatus = (status || 'unknown').toLowerCase();

  switch (normStatus) {
    case 'fresh':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${className}`}
          title="Live real-time data fetched from authoritative external API"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          {label || 'Live Fresh'}
        </span>
      );
    case 'cached':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 ${className}`}
          title="Served from high-speed in-memory TTL cache"
        >
          <Clock className="w-3 h-3 text-cyan-400" />
          {label || 'Cached'}
        </span>
      );
    case 'database':
    case 'success':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 ${className}`}
          title="Verified canonical record from MongoDB Atlas"
        >
          <Database className="w-3 h-3 text-indigo-400" />
          {label || 'Database'}
        </span>
      );
    case 'unavailable':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 ${className}`}
          title="Explicitly unavailable in authoritative upstream provider"
        >
          <AlertTriangle className="w-3 h-3 text-amber-400" />
          {label || 'Unavailable'}
        </span>
      );
    case 'error':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20 ${className}`}
          title="Upstream provider error"
        >
          <XCircle className="w-3 h-3 text-rose-400" />
          {label || 'Error'}
        </span>
      );
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700 ${className}`}
        >
          <Sparkles className="w-3 h-3 text-slate-400" />
          {label || normStatus}
        </span>
      );
  }
};
