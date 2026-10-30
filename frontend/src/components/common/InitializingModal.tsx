import React, { useState, useEffect } from 'react';
import { useUrban } from '../../context/UrbanContext.tsx';
import { Activity, MapPin } from 'lucide-react';

export const InitializingModal: React.FC = () => {
  const { isInitializingCity, initializingCityName } = useUrban();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const steps = [
    'CONNECTING TO SATELLITE & SENSOR ARRAYS...',
    'INITIALIZING SPATIAL TWIN TOPOLOGY...',
    'ANALYZING MULTI-MODAL TRAFFIC SIGNALS...',
    'SYNCING URBAN ENERGY & ENVIRONMENTAL TELEMETRY...',
    'ENGAGING PARTICLE SWARM OPTIMIZER...',
    'CITY INTELLIGENCE OPERATIONAL.'
  ];

  useEffect(() => {
    if (!isInitializingCity) {
      setCurrentStepIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev + 1 < steps.length ? prev + 1 : prev));
    }, 200);
    return () => clearInterval(interval);
  }, [isInitializingCity, steps.length]);

  if (!isInitializingCity) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-md p-8 rounded-2xl bg-[#0B1726] border border-cyan-500/50 shadow-[0_0_50px_rgba(34,211,238,0.25)] flex flex-col items-center text-center">
        {/* Animated Cyber Core Ring */}
        <div className="relative w-20 h-20 mb-6 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-2 border-cyan-500/20" />
          <div className="absolute inset-0 rounded-full border-t-2 border-r-2 border-cyan-400 animate-spin" />
          <div className="absolute inset-2 rounded-full border-b-2 border-l-2 border-purple-500 animate-spin" style={{ animationDirection: 'reverse', animationDuration: '3s' }} />
          <MapPin className="w-8 h-8 text-cyan-400 animate-pulse" />
        </div>

        <div className="text-[11px] font-mono tracking-widest text-cyan-400 font-bold uppercase mb-1">
          INITIALIZING CITY INTELLIGENCE
        </div>
        <h2 className="text-2xl font-black text-white font-mono tracking-tight uppercase mb-3">
          {initializingCityName || 'URBAN GRID'}
        </h2>

        {/* Progress Bar */}
        <div className="w-full h-1.5 rounded-full bg-slate-900 border border-[#1E334A] overflow-hidden mb-4">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 transition-all duration-200"
            style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
          />
        </div>

        {/* Dynamic Telemetry Log */}
        <div className="text-xs font-mono text-slate-300 min-h-[24px] flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span className="truncate">{steps[currentStepIndex]}</span>
        </div>

        <div className="mt-4 pt-4 border-t border-[#1E334A] w-full flex items-center justify-between text-[10px] font-mono text-slate-400">
          <span>LATENCY: 1.4ms</span>
          <span className="text-emerald-400">ENCRYPTION: QUANTUM COHERENT</span>
        </div>
      </div>
    </div>
  );
};
