import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import {
  Radio,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const LivePulsePage: React.FC = () => {
  const { pulseStreams, currentCity, navigate } = useUrban();
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = ['ALL', 'TRAFFIC', 'AIR QUALITY', 'ENERGY', 'WATER', 'TRANSIT'];

  const filteredStreams = selectedCategory === 'ALL'
    ? pulseStreams
    : pulseStreams.filter((s: any) => s.category === selectedCategory);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span>CITY MARKET DATA PROTOCOL</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            LIVE URBAN PULSE STREAM
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Real-time multi-frequency telemetry exchange monitoring municipal velocity, grid power consumption, atmospheric particulate matter, and transit flow for {currentCity.name}.
          </p>
        </div>

        {/* Global Connection Telemetry */}
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-right">
            <div className="text-[10px] font-mono text-slate-400">NETWORK INGESTION</div>
            <div className="text-sm font-bold font-mono text-emerald-400">14.2 MB/s STREAM</div>
          </div>
          <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-right">
            <div className="text-[10px] font-mono text-slate-400">TIMESTAMP</div>
            <div className="text-sm font-bold font-mono text-cyan-400">LIVE SYNC</div>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#0B1726] border border-[#1E334A] overflow-x-auto scrollbar-none w-fit">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors whitespace-nowrap ${
              selectedCategory === cat
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Big City Market Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredStreams.map((stream: any) => {
          const isUp = stream.trend === 'up';

          const minV = Math.min(...stream.sparkline);
          const maxV = Math.max(...stream.sparkline);
          const rng = maxV - minV || 1;
          const pts = stream.sparkline
            .map((v: any, i: number) => {
              const x = (i / (stream.sparkline.length - 1)) * 260;
              const y = 60 - ((v - minV) / rng) * 45;
              return `${x},${y}`;
            })
            .join(' ');

          return (
            <div
              key={stream.id}
              className="rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] hover:border-cyan-500/50 p-6 transition-all duration-200 shadow-xl space-y-5"
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold font-mono text-slate-400 uppercase tracking-wider">
                    {stream.category}
                  </span>
                  <h3 className="text-lg font-bold text-white font-mono mt-0.5">
                    {stream.name}
                  </h3>
                </div>
                <DataTrustBadge status={stream.trust} size="md" />
              </div>

              {/* Value and Delta */}
              <div className="flex items-baseline justify-between pt-2">
                <div>
                  <span className="text-3xl sm:text-4xl font-extrabold text-white font-mono tabular-nums">
                    {stream.currentValue}
                  </span>
                  <span className="text-xs text-slate-400 ml-2 font-mono">
                    {stream.unit}
                  </span>
                </div>

                <div className={`flex items-center gap-1 text-sm font-mono font-bold ${isUp ? 'text-cyan-400' : 'text-amber-400'}`}>
                  {isUp ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  <span>{stream.delta}</span>
                </div>
              </div>

              {/* Large Market Sparkline Canvas */}
              <div className="w-full h-16 bg-[#07111F] rounded-xl border border-[#1E334A] p-2 flex items-center justify-center">
                <svg viewBox="0 0 260 60" className="w-full h-full overflow-visible">
                  <polyline
                    fill="none"
                    stroke={isUp ? '#22D3EE' : '#F59E0B'}
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={pts}
                  />
                </svg>
              </div>

              {/* Technical Telemetry Metadata */}
              <div className="space-y-1.5 pt-2 border-t border-[#1E334A] text-xs font-mono text-slate-400">
                <div className="flex justify-between">
                  <span>SENSOR SOURCE</span>
                  <span className="text-slate-200 truncate max-w-[180px]">{stream.source}</span>
                </div>
                <div className="flex justify-between">
                  <span>PACKET TIMESTAMP</span>
                  <span className="text-cyan-400">{stream.timestamp}</span>
                </div>
                <div className="flex justify-between">
                  <span>OPERATIONAL STATUS</span>
                  <span className="text-emerald-400 font-semibold">{stream.status}</span>
                </div>
              </div>

              {/* Action */}
              <button
                onClick={() => navigate('spatial')}
                className="w-full py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-cyan-300 text-xs font-mono font-semibold transition-colors flex items-center justify-center gap-1.5"
              >
                <span>LOCATE CORRIDOR TELEMETRY</span>
                <span className="text-cyan-400">→</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
