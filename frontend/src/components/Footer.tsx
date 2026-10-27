import React from 'react';
import { ShieldCheck, Cpu, Database, Compass, Globe } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950/90 text-slate-400 py-12 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white">
                <Compass className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-100 tracking-tight text-base">
                UrbanLens Intelligence
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-md">
              A high-precision, multi-agent urban intelligence platform. Grounded in verified MongoDB Atlas census data, real-time Open-Meteo & OpenAQ sensors, and dense RAG evidence synthesis.
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero-Fabrication Guarantee: Grounded Evidence Only</span>
            </div>
          </div>

          {/* Architecture Pillars */}
          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">
              Platform Architecture
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li className="flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                <span>7 Domain Intelligence Agents</span>
              </li>
              <li className="flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-cyan-400" />
                <span>MongoDB Atlas Canonical Store</span>
              </li>
              <li className="flex items-center gap-2">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>Open-Meteo & OpenAQ Live Providers</span>
              </li>
              <li className="flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                <span>Groq Llama-3 Reasoning Layer</span>
              </li>
            </ul>
          </div>

          {/* Core Endpoints */}
          <div>
            <h4 className="text-xs font-semibold text-slate-200 uppercase tracking-wider mb-3">
              System Endpoints
            </h4>
            <ul className="space-y-2 text-xs text-slate-400 font-mono">
              <li>/api/v1/cities</li>
              <li>/api/v1/cities/{'{id}'}/weather/live</li>
              <li>/api/v1/cities/{'{id}'}/air-quality</li>
              <li>/api/v1/intelligence/ask</li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <p>© {new Date().getFullYear()} UrbanLens Platform. Built for autonomous urban analytics.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              FastAPI + React 19 + TypeScript
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
