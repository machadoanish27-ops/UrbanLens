import React from 'react';
import { useUrban } from '../context/UrbanContext';
import { PREDICTIONS_DATA } from '../data/urbanData';
import { TrendingUp, Clock, Cpu, Sparkles } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const PredictionsPage: React.FC = () => {
  const { currentCity, navigate, toggleAiModal } = useUrban();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-purple-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-purple-400" />
            <span>PREDICTIVE URBAN INTELLIGENCE</span>
            <span>·</span>
            <DataTrustBadge status="PREDICTED" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            FORECAST & RISK HORIZONS
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Machine learning predictive pipelines trained on historical traffic dynamics, coastal meteorological soundings, and tidal sensor arrays for {currentCity.name}.
          </p>
        </div>

        <button
          onClick={() => toggleAiModal(true)}
          className="px-4 py-2.5 rounded-xl bg-purple-950/60 border border-purple-500/40 hover:border-purple-400 text-purple-300 text-xs font-mono font-bold tracking-wider transition-all flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          <span>RUN PREDICTIVE INFERENCE</span>
        </button>
      </div>

      {/* Predictions Cards Grid (Section 13) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {PREDICTIONS_DATA.map((pred) => (
          <div
            key={pred.id}
            className="rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] hover:border-purple-500/50 p-6 transition-all duration-200 shadow-xl flex flex-col justify-between space-y-6"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#07111F] text-slate-400 border border-[#1E334A]">
                  {pred.category}
                </span>
                <DataTrustBadge status="PREDICTED" size="sm" />
              </div>

              <div>
                <div className="text-[11px] font-mono text-purple-400 font-semibold flex items-center gap-1.5 mb-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>HORIZON: {pred.timeHorizon}</span>
                </div>
                <h3 className="text-lg font-bold font-mono text-white leading-snug">
                  {pred.title}
                </h3>
              </div>

              {/* Prediction Value Box */}
              <div className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-500/30">
                <div className="text-[10px] font-mono text-slate-400 uppercase">PROJECTED STATE</div>
                <div className="text-sm font-bold font-mono text-purple-300 mt-1">
                  {pred.predictionValue}
                </div>
              </div>

              {/* Confidence Gauge */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="text-slate-400">MODEL CONFIDENCE</span>
                  <span className="text-cyan-400 font-bold">{pred.confidence}%</span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full"
                    style={{ width: `${pred.confidence}%` }}
                  />
                </div>
              </div>

              {/* Signals Used */}
              <div>
                <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold mb-2">
                  TELEMETRY SIGNALS CONSUMED
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {pred.signalsUsed.map((sig, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 rounded-md bg-[#07111F] border border-[#1E334A] text-[10px] font-mono text-slate-300"
                    >
                      {sig}
                    </span>
                  ))}
                </div>
              </div>

              <p className="text-xs text-slate-300 font-sans leading-relaxed pt-2 border-t border-[#1E334A]">
                {pred.impactAssessment}
              </p>
            </div>

            {/* Bottom Action */}
            {(pred as any).mitigationAvailable ? (
              <button
                onClick={() => navigate('optimization')}
                className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold transition-all flex items-center justify-center gap-1.5 shadow-md"
              >
                <Cpu className="w-3.5 h-3.5" />
                <span>PRE-EMPT WITH PSO SWARM</span>
              </button>
            ) : (
              <div className="text-center text-[11px] font-mono text-slate-400 py-2 border-t border-[#1E334A]">
                Within safe municipal variance · Standby monitoring
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
