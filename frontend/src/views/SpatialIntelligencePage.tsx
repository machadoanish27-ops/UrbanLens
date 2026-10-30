import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { CityMapCanvas } from '../components/common/CityMapCanvas';
import {
  Layers,
  Sparkles,
  Cpu,
  Eye,
  Crosshair,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const SpatialIntelligencePage: React.FC = () => {
  const { currentCity, selectedZone, toggleAiModal, navigate } = useUrban();

  const [activeLayers, setActiveLayers] = useState<Record<string, boolean>>({
    traffic: true,
    aqi: true,
    energy: true,
    water: false,
    infrastructure: true,
    population: true,
    anomalies: true,
    riskZones: true,
    optimizationRoutes: true,
  });

  const layerList = [
    { id: 'traffic', label: 'Traffic Mobility Flow', color: 'text-cyan-400' },
    { id: 'aqi', label: 'Air Quality (AQI Dispersion)', color: 'text-purple-400' },
    { id: 'population', label: 'Human Density & Footfall', color: 'text-blue-400' },
    { id: 'infrastructure', label: 'Transit & Utility Arterials', color: 'text-slate-300' },
    { id: 'energy', label: 'Micro-Grid Electrical Demand', color: 'text-amber-400' },
    { id: 'water', label: 'Hydraulic Pressure Telemetry', color: 'text-teal-400' },
    { id: 'anomalies', label: 'AI Spatial Anomalies', color: 'text-rose-400' },
    { id: 'riskZones', label: 'Predicted Flood & Choke Zones', color: 'text-amber-400' },
    { id: 'optimizationRoutes', label: 'PSO Swarm Optimal Vectors', color: 'text-emerald-400' },
  ];

  const toggleLayer = (id: string) => {
    setActiveLayers((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl px-6 py-4">
        <div>
          <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <span>SPATIAL COMMAND ENVIRONMENT</span>
            <span>·</span>
            <span>FULL 3D TOPOLOGY MATRIX</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black font-mono text-white tracking-tight uppercase">
            {currentCity.name} Spatial Intelligence Desk
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <DataTrustBadge status="LIVE" size="md" />
          <button
            onClick={() => toggleAiModal(true)}
            className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-mono font-bold tracking-wider transition-all flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>ASK AI</span>
          </button>
        </div>
      </div>

      {/* 3-Column Layout: Left Controls, Center Map, Right Intelligence */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left: Layer Controls (3 Cols) */}
        <div className="lg:col-span-3 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 border-b border-[#1E334A] pb-3 mb-3">
              <Layers className="w-4 h-4 text-cyan-400" />
              <h2 className="text-xs font-bold font-mono text-white uppercase tracking-wider">
                TOPOLOGICAL LAYERS
              </h2>
            </div>

            <div className="space-y-1.5">
              {layerList.map((layer) => {
                const isActive = activeLayers[layer.id];

                return (
                  <button
                    key={layer.id}
                    onClick={() => toggleLayer(layer.id)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl text-xs font-mono transition-colors text-left ${
                      isActive
                        ? 'bg-[#07111F] border border-cyan-500/40 text-white'
                        : 'text-slate-400 hover:bg-[#07111F]/50 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <span className={`w-2 h-2 rounded-full ${isActive ? 'bg-cyan-400' : 'bg-slate-600'}`} />
                      <span className="truncate">{layer.label}</span>
                    </div>
                    <Eye className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-600'}`} />
                  </button>
                );
              })}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-[10px] font-mono text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>SATELLITE SYNC</span>
              <span className="text-emerald-400 font-bold">LIDAR 100%</span>
            </div>
            <div className="flex justify-between">
              <span>ACTIVE NODES</span>
              <span className="text-white">2,854 SENSORS</span>
            </div>
          </div>
        </div>

        {/* Center: Large Spatial Map with Timeline (6 Cols) */}
        <div className="lg:col-span-6 space-y-2">
          <CityMapCanvas heightClass="h-[620px]" showTimeline={true} />
        </div>

        {/* Right: Operational Intelligence Panel (3 Cols) */}
        <div className="lg:col-span-3 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-[#1E334A] pb-3 mb-3">
              <div className="flex items-center gap-2">
                <Crosshair className="w-4 h-4 text-cyan-400" />
                <h2 className="text-xs font-bold font-mono text-white uppercase tracking-wider">
                  ZONE INSPECTOR
                </h2>
              </div>
              <DataTrustBadge status="LIVE" size="sm" />
            </div>

            {selectedZone ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-bold font-mono text-white uppercase">
                    {selectedZone.name}
                  </h3>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                    COORDINATES: [{selectedZone.coordinates.join(', ')}]
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                    <div className="text-[9px] text-slate-400">FLOW DENSITY</div>
                    <div className="text-base font-bold text-white mt-0.5">{selectedZone.traffic}%</div>
                    <div className="text-[10px] text-amber-400">{selectedZone.trafficDelta}</div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                    <div className="text-[9px] text-slate-400">AQI INDEX</div>
                    <div className="text-base font-bold text-purple-300 mt-0.5">{selectedZone.aqi}</div>
                    <div className="text-[10px] text-slate-400">Micro-sensor</div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                    <div className="text-[9px] text-slate-400">ENERGY DEMAND</div>
                    <div className="text-base font-bold text-cyan-300 mt-0.5">{selectedZone.energyDelta}</div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                    <div className="text-[9px] text-slate-400">TRANSIT LOAD</div>
                    <div className="text-base font-bold text-emerald-300 mt-0.5">{selectedZone.transitLoad}%</div>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-purple-950/20 border border-purple-500/30 text-xs">
                  <div className="text-[10px] font-mono text-purple-300 font-bold uppercase mb-1">
                    AI SIGNAL CORRELATION ({selectedZone.confidence}% CONF)
                  </div>
                  <p className="text-slate-200 text-xs leading-relaxed">
                    {selectedZone.aiSignal}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-xs">
                  <div className="text-[10px] font-mono text-cyan-300 font-bold uppercase mb-1">
                    RECOMMENDED DISPATCH
                  </div>
                  <p className="text-slate-200 text-xs leading-relaxed">
                    {selectedZone.recommendation}
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-6 text-center text-xs font-mono text-slate-400">
                Click any zone marker on the central map to inspect detailed spatial telemetry.
              </div>
            )}
          </div>

          <div className="space-y-2 pt-4 border-t border-[#1E334A]">
            <button
              onClick={() => navigate('optimization')}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold transition-all shadow-md flex items-center justify-center gap-2"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>OPTIMIZE SELECTED ZONE</span>
            </button>
            <button
              onClick={() => toggleAiModal(true)}
              className="w-full py-2.5 rounded-xl bg-[#07111F] border border-cyan-500/40 hover:border-cyan-400 text-cyan-300 text-xs font-mono font-semibold transition-colors flex items-center justify-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>DEEP REASONING QUERY</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
