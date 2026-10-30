import React from 'react';

export type TrustStatus =
  | 'VERIFIED'
  | 'LIVE'
  | 'PREDICTED'
  | 'INFERENCE'
  | 'SIMULATION'
  | 'CACHED'
  | 'DATA UNAVAILABLE';

interface DataTrustBadgeProps {
  status: TrustStatus | string;
  size?: 'sm' | 'md';
  provider?: string;
  source?: string;
}

export const DataTrustBadge: React.FC<DataTrustBadgeProps> = ({ status, size = 'sm', provider, source }) => {
  const normStatus = (status || 'VERIFIED').toUpperCase();
  const displayProvider = provider || source;

  const getBadgeStyle = () => {
    switch (normStatus) {
      case 'LIVE':
      case 'FRESH':
        return 'text-emerald-400 bg-emerald-950/40 border-emerald-500/30';
      case 'VERIFIED':
      case 'CANONICAL':
        return 'text-cyan-400 bg-cyan-950/40 border-cyan-500/30';
      case 'CACHED':
        return 'text-blue-400 bg-blue-950/40 border-blue-500/30';
      case 'PREDICTED':
      case 'DERIVED':
        return 'text-purple-400 bg-purple-950/40 border-purple-500/30';
      case 'INFERENCE':
      case 'LLM_SYNTHESIS':
        return 'text-amber-400 bg-amber-950/40 border-amber-500/30';
      case 'DATA UNAVAILABLE':
      case 'UNAVAILABLE':
        return 'text-rose-400 bg-rose-950/40 border-rose-500/30';
      default:
        return 'text-slate-400 bg-slate-900 border-slate-700';
    }
  };

  const getIndicator = () => {
    switch (normStatus) {
      case 'LIVE':
      case 'FRESH':
        return '●';
      case 'VERIFIED':
      case 'CANONICAL':
        return '✓';
      case 'CACHED':
        return '◷';
      case 'PREDICTED':
      case 'DERIVED':
        return '◈';
      case 'INFERENCE':
      case 'LLM_SYNTHESIS':
        return '✦';
      case 'DATA UNAVAILABLE':
      case 'UNAVAILABLE':
        return '✕';
      default:
        return '•';
    }
  };

  const pad = size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-medium tracking-wider rounded border ${pad} ${getBadgeStyle()} transition-colors duration-150 whitespace-nowrap shrink-0`}
      title={displayProvider ? `Source: ${displayProvider} (${normStatus})` : `Data state: ${normStatus}`}
    >
      <span className="text-[9px] opacity-90">{getIndicator()}</span>
      <span>{normStatus}</span>
      {displayProvider && <span className="opacity-60 text-[9px]">· {displayProvider}</span>}
    </span>
  );
};
