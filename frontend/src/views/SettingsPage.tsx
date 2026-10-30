import React from 'react';
import { useUrban } from '../context/UrbanContext.tsx';
import {
  Settings,
  User,
  Palette,
  Database,
  Bell,
  Sparkles,
  MapPin,
  Ruler,
  Lock,
  Info,
  CheckCircle2
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { activeSettingsTab, setActiveSettingsTab, user } = useUrban();

  const tabs = [
    { id: 'profile', label: 'Operator Profile', icon: User },
    { id: 'appearance', label: 'Appearance & HUD', icon: Palette },
    { id: 'data', label: 'Data & Telemetry Preferences', icon: Database },
    { id: 'notifications', label: 'Alert Notification Rules', icon: Bell },
    { id: 'ai', label: 'AI Reasoning Parameters', icon: Sparkles },
    { id: 'map', label: 'Spatial Map Engine', icon: MapPin },
    { id: 'units', label: 'Measurement Units', icon: Ruler },
    { id: 'privacy', label: 'Security & Access Keys', icon: Lock },
    { id: 'about', label: 'About UrbanLens OS', icon: Info },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
          <Settings className="w-4 h-4 text-cyan-400" />
          <span>SYSTEM CONFIGURATION CONSOLE</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
          Settings & Preferences
        </h1>
        <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
          Configure multi-spectral telemetry polling frequencies, spatial visualization shaders, and operator role security parameters.
        </p>
      </div>

      {/* Settings Layout: Left Tabs (3 Cols) + Right Form Content (9 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Tabs */}
        <div className="lg:col-span-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] p-3 space-y-1">
          {tabs.map((tab) => {
            const IconComp = tab.icon;
            const isActive = activeSettingsTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveSettingsTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-mono transition-colors text-left ${
                  isActive
                    ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/40 font-bold shadow-md'
                    : 'text-slate-400 hover:text-white hover:bg-[#07111F]'
                }`}
              >
                <IconComp className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span className="truncate">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right Settings Form Container */}
        <div className="lg:col-span-8 rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-6">
          {/* Profile Tab */}
          {activeSettingsTab === 'profile' && (
            <div className="space-y-5">
              <h3 className="text-base font-bold font-mono text-white uppercase border-b border-[#1E334A] pb-3">
                Operator Identity Details
              </h3>
              <div className="flex items-center gap-4">
                <img
                  src={user.avatarUrl}
                  alt={user.name}
                  className="w-16 h-16 rounded-xl border-2 border-cyan-500/40 object-cover"
                />
                <div>
                  <h4 className="text-sm font-bold font-mono text-white">{user.name}</h4>
                  <p className="text-xs text-slate-400 font-mono">{user.role}</p>
                  <p className="text-[10px] text-cyan-400 font-mono mt-0.5">{user.organization}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
                <div>
                  <label className="text-slate-400 text-[10px] uppercase">OPERATIONAL EMAIL</label>
                  <input
                    type="text"
                    disabled
                    value={user.email}
                    className="w-full mt-1 px-3 py-2 rounded-lg bg-[#07111F] border border-[#1E334A] text-slate-300"
                  />
                </div>
                <div>
                  <label className="text-slate-400 text-[10px] uppercase">SECURITY CLEARANCE</label>
                  <input
                    type="text"
                    disabled
                    value="LEVEL 4 (SUPER-ADMIN)"
                    className="w-full mt-1 px-3 py-2 rounded-lg bg-[#07111F] border border-[#1E334A] text-emerald-400 font-bold"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Appearance Tab */}
          {activeSettingsTab === 'appearance' && (
            <div className="space-y-5">
              <h3 className="text-base font-bold font-mono text-white uppercase border-b border-[#1E334A] pb-3">
                Visual HUD & Cybernetic Aesthetics
              </h3>
              <div className="space-y-3 text-xs font-mono text-slate-300">
                <label className="flex items-center justify-between p-3 rounded-xl bg-[#07111F] border border-[#1E334A] cursor-pointer">
                  <span>Atmospheric Spatial Grid Coordinates</span>
                  <input type="checkbox" defaultChecked className="accent-cyan-400 w-4 h-4" />
                </label>
                <label className="flex items-center justify-between p-3 rounded-xl bg-[#07111F] border border-[#1E334A] cursor-pointer">
                  <span>Pulse Scanline Simulation Glow</span>
                  <input type="checkbox" defaultChecked className="accent-cyan-400 w-4 h-4" />
                </label>
                <label className="flex items-center justify-between p-3 rounded-xl bg-[#07111F] border border-[#1E334A] cursor-pointer">
                  <span>High-Contrast Monospace Tabular Figures</span>
                  <input type="checkbox" defaultChecked className="accent-cyan-400 w-4 h-4" />
                </label>
              </div>
            </div>
          )}

          {/* Data Preferences */}
          {activeSettingsTab === 'data' && (
            <div className="space-y-5">
              <h3 className="text-base font-bold font-mono text-white uppercase border-b border-[#1E334A] pb-3">
                Telemetry Streaming Frequencies
              </h3>
              <div className="space-y-3 text-xs font-mono text-slate-300">
                <div>
                  <label className="text-[10px] text-slate-400 uppercase">LIVE PULSE POLLING INTERVAL</label>
                  <select className="w-full mt-1 px-3 py-2 rounded-lg bg-[#07111F] border border-[#1E334A] text-white">
                    <option>4 Seconds (Real-time live jitter)</option>
                    <option>10 Seconds (Bandwidth conservation)</option>
                    <option>30 Seconds (Standard telemetry)</option>
                  </select>
                </div>
                <label className="flex items-center justify-between p-3 rounded-xl bg-[#07111F] border border-[#1E334A] cursor-pointer">
                  <span>Strict Data Honesty Mode (Never fabricate missing values)</span>
                  <input type="checkbox" defaultChecked disabled className="accent-cyan-400 w-4 h-4" />
                </label>
              </div>
            </div>
          )}

          {/* About UrbanLens */}
          {activeSettingsTab === 'about' && (
            <div className="space-y-4">
              <h3 className="text-base font-bold font-mono text-white uppercase border-b border-[#1E334A] pb-3">
                UrbanLens Architecture
              </h3>
              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                UrbanLens is an enterprise Urban Intelligence Operating System combining smart city sensor infrastructure,
                spatial coordinate grids, multimodal AI reasoning, particle swarm heuristics, and 127-qubit quantum annealing algorithms.
              </p>
              <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs font-mono space-y-1.5 text-slate-300">
                <div>VERSION: <span className="text-cyan-400 font-bold">4.2.0-ENTERPRISE-PRO</span></div>
                <div>FRAMEWORK: <span className="text-white">React 19 + TypeScript + Tailwind CSS</span></div>
                <div>QUANTUM CORE: <span className="text-purple-400">Superconducting Transmon DR-7</span></div>
                <div>SECURITY: <span className="text-emerald-400">Post-Quantum Cryptographic TLS 1.3</span></div>
              </div>
            </div>
          )}

          {/* Other tabs fallback */}
          {!['profile', 'appearance', 'data', 'about'].includes(activeSettingsTab) && (
            <div className="space-y-4">
              <h3 className="text-base font-bold font-mono text-white uppercase border-b border-[#1E334A] pb-3">
                {tabs.find(t => t.id === activeSettingsTab)?.label}
              </h3>
              <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs font-mono text-slate-300 space-y-2">
                <div className="text-emerald-400 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Configured to operational baseline standards.</span>
                </div>
                <p className="text-slate-400">
                  Settings are continuously persisted to local encrypted state and synced with enterprise policy.
                </p>
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-[#1E334A] flex justify-end">
            <button
              onClick={() => alert('Configuration preferences saved to secure enclave.')}
              className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono font-bold text-xs transition-colors shadow-lg"
            >
              SAVE CONFIGURATION
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
