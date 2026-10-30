import React, { useState } from 'react';
import type { LucideIcon } from 'lucide-react';
import { DataTrustBadge, type TrustStatus } from './DataTrustBadge';

interface MetricCardProps {
  title: string;
  value: string;
  unit: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: LucideIcon;
  sparkline?: number[];
  source?: string;
  updateTime?: string;
  trust?: TrustStatus | string;
  accentColor?: 'cyan' | 'blue' | 'violet' | 'amber' | 'emerald' | 'rose';
  detailNote?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  change,
  trend = 'neutral',
  icon: Icon,
  sparkline = [20, 22, 21, 24, 25, 26, 25],
  source,
  trust = 'VERIFIED',
  accentColor = 'cyan',
  detailNote,
  onClick,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getAccentBorder = () => {
    switch (accentColor) {
      case 'cyan': return 'hover:border-cyan-500/50 hover:shadow-[0_0_24px_rgba(34,211,238,0.15)]';
      case 'blue': return 'hover:border-blue-500/50 hover:shadow-[0_0_24px_rgba(59,130,246,0.15)]';
      case 'violet': return 'hover:border-purple-500/50 hover:shadow-[0_0_24px_rgba(139,92,246,0.15)]';
      case 'amber': return 'hover:border-amber-500/50 hover:shadow-[0_0_24px_rgba(245,158,11,0.15)]';
      case 'emerald': return 'hover:border-emerald-500/50 hover:shadow-[0_0_24px_rgba(16,185,129,0.15)]';
      case 'rose': return 'hover:border-rose-500/50 hover:shadow-[0_0_24px_rgba(239,68,68,0.15)]';
      default: return 'hover:border-cyan-500/50';
    }
  };

  const getIconColor = () => {
    switch (accentColor) {
      case 'cyan': return 'text-cyan-400 bg-cyan-950/40 border-cyan-500/30';
      case 'blue': return 'text-blue-400 bg-blue-950/40 border-blue-500/30';
      case 'violet': return 'text-purple-400 bg-purple-950/40 border-purple-500/30';
      case 'amber': return 'text-amber-400 bg-amber-950/40 border-amber-500/30';
      case 'emerald': return 'text-emerald-400 bg-emerald-950/40 border-emerald-500/30';
      case 'rose': return 'text-rose-400 bg-rose-950/40 border-rose-500/30';
      default: return 'text-cyan-400 bg-cyan-950/40 border-cyan-500/30';
    }
  };

  // Sparkline points
  const minVal = Math.min(...sparkline);
  const maxVal = Math.max(...sparkline);
  const range = maxVal - minVal || 1;
  const points = sparkline
    .map((v, i) => {
      const x = (i / (sparkline.length - 1)) * 90;
      const y = 30 - ((v - minVal) / range) * 24;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      className={`group relative rounded-2xl bg-[#0B1726]/80 backdrop-blur-md border border-[#1E334A] p-5 transition-all duration-300 ${getAccentBorder()} cursor-pointer overflow-hidden flex flex-col justify-between`}
    >
      <div
        className={`absolute top-0 left-0 right-0 h-[2px] opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r ${
          accentColor === 'violet' ? 'from-purple-500 to-fuchsia-500' :
          accentColor === 'amber' ? 'from-amber-500 to-rose-500' :
          accentColor === 'emerald' ? 'from-emerald-500 to-teal-500' :
          'from-cyan-500 to-blue-500'
        }`}
      />

      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl border ${getIconColor()} group-hover:scale-110 transition-transform duration-200`}>
              <Icon className="w-4 h-4" />
            </div>
            <span className="text-xs font-mono font-bold tracking-wide text-slate-300 uppercase">
              {title}
            </span>
          </div>
          <DataTrustBadge status={trust} size="sm" />
        </div>

        <div className="flex items-baseline justify-between mt-1">
          <div>
            <div className="text-2xl sm:text-3xl font-black font-mono text-white tracking-tight tabular-nums">
              {value}
            </div>
            <div className="text-[11px] font-mono text-slate-400 mt-0.5">
              {unit}
            </div>
          </div>

          <div className="w-20 h-8 shrink-0">
            <svg viewBox="0 0 90 32" className="w-full h-full overflow-visible">
              <polyline
                fill="none"
                stroke={
                  accentColor === 'rose' ? '#EF4444' :
                  accentColor === 'amber' ? '#F59E0B' :
                  accentColor === 'emerald' ? '#10B981' :
                  accentColor === 'violet' ? '#A855F7' : '#22D3EE'
                }
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={points}
              />
            </svg>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-[#1E334A]/60 flex items-center justify-between text-[10px] font-mono text-slate-400">
        <span className="truncate max-w-[140px]">{source || 'UrbanLens Canonical DB'}</span>
        {change && (
          <span className={`font-semibold ${trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-slate-400'}`}>
            {change}
          </span>
        )}
      </div>

      {detailNote && isHovered && (
        <div className="absolute inset-x-0 bottom-0 bg-[#07111F]/95 backdrop-blur-md p-3 border-t border-[#1E334A] text-[10px] font-mono text-slate-300 animate-in fade-in duration-150 z-20">
          {detailNote}
        </div>
      )}
    </div>
  );
};
