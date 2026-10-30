import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import {
  BarChart3,
  Scale,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const AnalyticsPage: React.FC = () => {
  const { currentCity, navigate } = useUrban();
  const [activeTab, setActiveTab] = useState<'mobility' | 'environment' | 'population' | 'education' | 'economic'>('mobility');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '1y'>('7d');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <span>METROPOLITAN TELEMETRY ANALYTICS</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Deep Analytics
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Single-question analytical charts with zero-pill discipline, precise tabular figures, and multi-variable historical tracking.
          </p>
        </div>

        {/* Date Range Selector & Export */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1 p-1 rounded-xl bg-[#07111F] border border-[#1E334A]">
            {(['24h', '7d', '30d', '1y'] as const).map((r) => (
              <button
                key={r}
                onClick={() => setTimeRange(r)}
                className={`px-3 py-1 text-xs font-mono rounded-lg transition-colors ${
                  timeRange === r
                    ? 'bg-cyan-500 text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {r.toUpperCase()}
              </button>
            ))}
          </div>

          <button
            onClick={() => navigate('compare')}
            className="px-3.5 py-2 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-200 transition-colors flex items-center gap-1.5"
          >
            <Scale className="w-3.5 h-3.5 text-cyan-400" />
            <span>COMPARE CITIES</span>
          </button>
        </div>
      </div>

      {/* Domain Category Tabs */}
      <div className="flex items-center gap-2 border-b border-[#1E334A] pb-1 overflow-x-auto scrollbar-none">
        {[
          { id: 'mobility', label: 'Mobility & Corridor Flow' },
          { id: 'environment', label: 'Atmospheric & Climate' },
          { id: 'population', label: 'Demographics & Footfall' },
          { id: 'education', label: 'Higher Education & Research' },
          { id: 'economic', label: 'Economic & Cost Index' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 text-xs font-mono font-semibold transition-colors border-b-2 whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-cyan-400 text-cyan-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Clean Analytical Charts Grid (Section 14: One chart = one question, clean axes, minimal gridlines) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1 */}
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
            <div>
              <div className="text-xs font-mono text-slate-400 uppercase">RESEARCH QUESTION</div>
              <h3 className="text-sm font-bold font-mono text-white mt-0.5">
                How does vehicular density fluctuate across peak commuter hours?
              </h3>
            </div>
            <DataTrustBadge status="VERIFIED" size="sm" />
          </div>

          {/* SVG Bar / Line Representation */}
          <div className="h-64 flex flex-col justify-between pt-4">
            <div className="flex-1 flex items-end gap-3 px-2">
              {[
                { time: '06:00', val: 32 },
                { time: '08:00', val: 78 },
                { time: '10:00', val: 86 },
                { time: '12:00', val: 62 },
                { time: '14:00', val: 68 },
                { time: '16:00', val: 74 },
                { time: '18:00', val: 92 },
                { time: '20:00', val: 81 },
                { time: '22:00', val: 48 },
              ].map((item, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                  <div className="text-[10px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    {item.val}%
                  </div>
                  <div
                    className="w-full bg-cyan-950 border border-cyan-500/40 rounded-t-sm group-hover:bg-cyan-500 transition-colors"
                    style={{ height: `${item.val * 2}px` }}
                  />
                  <span className="text-[10px] font-mono text-slate-400">{item.time}</span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-[#1E334A] flex justify-between text-[11px] font-mono text-slate-400">
              <span>PEAK PERIOD: 18:00 (92% LOAD)</span>
              <span className="text-cyan-400">SAMPLE INTERVAL: 15 MIN</span>
            </div>
          </div>
        </div>

        {/* Chart 2 */}
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
            <div>
              <div className="text-xs font-mono text-slate-400 uppercase">RESEARCH QUESTION</div>
              <h3 className="text-sm font-bold font-mono text-white mt-0.5">
                What is the correlation between wind velocity and particulate matter?
              </h3>
            </div>
            <DataTrustBadge status="LIVE" size="sm" />
          </div>

          {/* Environmental Correlation Vector */}
          <div className="h-64 flex flex-col justify-between pt-4">
            <div className="flex-1 flex items-end gap-3 px-2">
              {[
                { day: 'Mon', aqi: 168, wind: 8 },
                { day: 'Tue', aqi: 154, wind: 12 },
                { day: 'Wed', aqi: 142, wind: 16 },
                { day: 'Thu', aqi: 161, wind: 9 },
                { day: 'Fri', aqi: 158, wind: 14 },
                { day: 'Sat', aqi: 135, wind: 18 },
                { day: 'Sun', aqi: 128, wind: 22 },
              ].map((item, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-2 group h-full justify-end">
                  <div className="text-[10px] font-mono text-purple-300 opacity-0 group-hover:opacity-100 transition-opacity">
                    AQI {item.aqi}
                  </div>
                  <div
                    className="w-full bg-purple-950 border border-purple-500/40 rounded-t-sm group-hover:bg-purple-500 transition-colors"
                    style={{ height: `${(item.aqi / 200) * 160}px` }}
                  />
                  <span className="text-[10px] font-mono text-slate-400">{item.day}</span>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-[#1E334A] flex justify-between text-[11px] font-mono text-slate-400">
              <span>INVERSE CORRELATION R = -0.78</span>
              <span className="text-purple-400">STRONG MARITIME DISPERSION</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
