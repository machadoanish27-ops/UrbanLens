import React from 'react';
import { useUrban } from '../context/UrbanContext';
import {
  CloudSun,
  Wind,
  Thermometer,
  Droplets,
  Activity,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const EnvironmentPage: React.FC = () => {
  const { currentCity } = useUrban();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <CloudSun className="w-4 h-4 text-cyan-400" />
            <span>METEOROLOGICAL & AIR SPECTROMETRY</span>
            <span>·</span>
            <DataTrustBadge status="LIVE" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Environmental Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Multi-spectral laser spectrometry monitoring particulates, nitrous oxides, ground ozone, and surface atmospheric dynamics.
          </p>
        </div>

        <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-right">
          <div className="text-[10px] font-mono text-slate-400">DISPERSION STATUS</div>
          <div className="text-sm font-bold font-mono text-cyan-400">COASTAL SEA BREEZE</div>
        </div>
      </div>

      {/* Surface Weather Parameters (Section 17) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Thermometer className="w-4 h-4 text-amber-400" />
            <span>TEMPERATURE</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-white mt-1">
            {currentCity.temperature}°C
          </div>
          <div className="text-xs text-slate-400 font-mono mt-1">
            Feels like {currentCity.feelsLike}°C
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Droplets className="w-4 h-4 text-blue-400" />
            <span>HUMIDITY</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-white mt-1">
            {currentCity.humidity}%
          </div>
          <div className="text-xs text-blue-400 font-mono mt-1">
            Dew point 24.2°C
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Wind className="w-4 h-4 text-cyan-400" />
            <span>SURFACE WIND</span>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold font-mono text-white mt-1 truncate">
            {currentCity.windSpeed}
          </div>
          <div className="text-xs text-cyan-400 font-mono mt-1">
            Gusts up to 21 km/h
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Activity className="w-4 h-4 text-purple-400" />
            <span>AIR QUALITY INDEX</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-purple-400 mt-1">
            AQI {currentCity.aqi}
          </div>
          <div className="text-xs text-slate-300 font-mono mt-1">
            {currentCity.aqiCategory}
          </div>
        </div>
      </div>

      {/* Atmospheric Gas Composition Array (Section 17) */}
      <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
          <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
            PARTICULATE & GAS SPECTROMETRY TELEMETRY
          </h2>
          <span className="text-[10px] font-mono text-slate-400">EPA & WHO STANDARDS</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>FINE PARTICLES (PM2.5)</span>
              <span className="text-purple-400 font-bold">{currentCity.pm25} µg/m³</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-purple-500 rounded-full"
                style={{ width: `${Math.min(100, (currentCity.pm25 / 150) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Target &lt; 15 µg/m³</div>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>COARSE PARTICLES (PM10)</span>
              <span className="text-amber-400 font-bold">{currentCity.pm10} µg/m³</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full"
                style={{ width: `${Math.min(100, (currentCity.pm10 / 200) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Target &lt; 45 µg/m³</div>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>NITROGEN DIOXIDE (NO₂)</span>
              <span className="text-cyan-400 font-bold">{currentCity.no2} ppb</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-cyan-400 rounded-full"
                style={{ width: `${Math.min(100, (currentCity.no2 / 100) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Vehicular combustion indicator</div>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>GROUND OZONE (O₃)</span>
              <span className="text-emerald-400 font-bold">{currentCity.o3} ppb</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-emerald-400 rounded-full"
                style={{ width: `${Math.min(100, (currentCity.o3 / 80) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Photochemical smog nominal</div>
          </div>
        </div>
      </div>
    </div>
  );
};
