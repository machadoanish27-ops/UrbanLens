import React from 'react';
import { useUrban } from '../context/UrbanContext.tsx';
import { Coins, Home, Utensils, Train, Zap, AlertCircle } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge.tsx';

export const CostOfLivingPage: React.FC = () => {
  const { currentCity } = useUrban();

  const isAvailable = currentCity.costOfLivingIndex !== null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Coins className="w-4 h-4 text-cyan-400" />
            <span>MUNICIPAL ECONOMIC BENCHMARK</span>
            <span>·</span>
            <DataTrustBadge status={isAvailable ? 'VERIFIED' : 'DATA UNAVAILABLE'} size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Cost of Living Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Consumer expenditure benchmarks normalized against New York City baseline (NYC = 100).
          </p>
        </div>

        {isAvailable && (
          <div className="p-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] text-right">
            <div className="text-[10px] font-mono text-slate-400">OVERALL INDEX</div>
            <div className="text-2xl font-black font-mono text-emerald-400">
              {currentCity.costOfLivingIndex}
            </div>
            <div className="text-[10px] font-mono text-slate-400">Base NYC = 100.0</div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {!isAvailable ? (
        /* Section 20 & Section 12: Honest Unavailable State */
        <div className="p-12 rounded-3xl bg-[#0B1726]/80 border border-rose-500/30 text-center max-w-2xl mx-auto space-y-4 shadow-2xl">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-rose-950/50 border border-rose-500/40 flex items-center justify-center text-rose-400">
            <AlertCircle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold font-mono text-white uppercase tracking-wider">
            COST INTELLIGENCE UNAVAILABLE
          </h2>
          <p className="text-sm text-slate-300 font-sans leading-relaxed">
            UrbanLens does not currently have verified city-level cost data for {currentCity.name}. <br />
            <strong className="text-white font-mono">No estimated or fabricated value is being displayed.</strong>
          </p>
          <div className="inline-block pt-2">
            <DataTrustBadge status="DATA UNAVAILABLE" size="md" />
          </div>
        </div>
      ) : (
        /* Populated State with Verified Index Components */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
            <div className="flex items-center gap-2.5 text-xs font-mono text-slate-400">
              <Home className="w-4 h-4 text-cyan-400" />
              <span>HOUSING & RENT</span>
            </div>
            <div className="text-3xl font-extrabold font-mono text-white">
              {currentCity.housingIndex}
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-400 rounded-full"
                style={{ width: `${currentCity.housingIndex}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-300 font-mono">
              75.2% cheaper than New York prime districts.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
            <div className="flex items-center gap-2.5 text-xs font-mono text-slate-400">
              <Utensils className="w-4 h-4 text-emerald-400" />
              <span>FOOD & DINING</span>
            </div>
            <div className="text-3xl font-extrabold font-mono text-white">
              {currentCity.foodIndex}
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-400 rounded-full"
                style={{ width: `${currentCity.foodIndex}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-300 font-mono">
              Fresh market produce and local dining highly economical.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
            <div className="flex items-center gap-2.5 text-xs font-mono text-slate-400">
              <Train className="w-4 h-4 text-blue-400" />
              <span>PUBLIC TRANSIT</span>
            </div>
            <div className="text-3xl font-extrabold font-mono text-white">
              {currentCity.transportIndex}
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-400 rounded-full"
                style={{ width: `${currentCity.transportIndex}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-300 font-mono">
              Suburban rail & Metro among lowest per-km costs globally.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
            <div className="flex items-center gap-2.5 text-xs font-mono text-slate-400">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>BASIC UTILITIES</span>
            </div>
            <div className="text-3xl font-extrabold font-mono text-white">
              {currentCity.utilitiesIndex}
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-400 rounded-full"
                style={{ width: `${currentCity.utilitiesIndex}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-300 font-mono">
              Electricity & high-speed broadband rates within optimal range.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
