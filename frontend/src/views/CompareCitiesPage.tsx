import React from 'react';
import { useUrban } from '../context/UrbanContext';
import { CITIES_DATA } from '../data/urbanData';
import { Scale, Users, Wind, Thermometer, Car, Coins, TrendingUp } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const CompareCitiesPage: React.FC = () => {
  const { currentCity, compareCityId, setCompareCityId } = useUrban();

  const cityA = currentCity;
  const cityB = CITIES_DATA[compareCityId] || CITIES_DATA['tokyo'];

  const metrics = [
    {
      label: 'Population',
      icon: Users,
      valA: cityA.population,
      valB: cityB.population,
      rawA: cityA.populationRaw,
      rawB: cityB.populationRaw,
      unit: 'people',
      lowerIsBetter: false,
    },
    {
      label: 'Air Quality (AQI)',
      icon: Wind,
      valA: `${cityA.aqi}`,
      valB: `${cityB.aqi}`,
      rawA: cityA.aqi,
      rawB: cityB.aqi,
      unit: 'Index',
      lowerIsBetter: true,
    },
    {
      label: 'Temperature',
      icon: Thermometer,
      valA: `${cityA.temperature}°C`,
      valB: `${cityB.temperature}°C`,
      rawA: cityA.temperature,
      rawB: cityB.temperature,
      unit: 'Celsius',
      lowerIsBetter: false,
    },
    {
      label: 'Traffic Load',
      icon: Car,
      valA: `${cityA.trafficLoad}%`,
      valB: `${cityB.trafficLoad}%`,
      rawA: cityA.trafficLoad,
      rawB: cityB.trafficLoad,
      unit: 'Load',
      lowerIsBetter: true,
    },
    {
      label: 'Transit Capacity Usage',
      icon: TrendingUp,
      valA: `${cityA.transitCapacity}%`,
      valB: `${cityB.transitCapacity}%`,
      rawA: cityA.transitCapacity,
      rawB: cityB.transitCapacity,
      unit: 'Usage',
      lowerIsBetter: false,
    },
    {
      label: 'Cost of Living Index',
      icon: Coins,
      valA: cityA.costOfLivingIndex ? `${cityA.costOfLivingIndex}` : 'UNAVAILABLE',
      valB: cityB.costOfLivingIndex ? `${cityB.costOfLivingIndex}` : 'UNAVAILABLE',
      rawA: cityA.costOfLivingIndex || 0,
      rawB: cityB.costOfLivingIndex || 0,
      unit: 'NYC=100',
      lowerIsBetter: true,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Scale className="w-4 h-4 text-cyan-400" />
            <span>CROSS-METROPOLITAN BENCHMARKING</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {cityA.name} vs {cityB.name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Normalized comparative telemetry matrix measuring mobility density, environmental impact, transit efficiency, and living expenditure.
          </p>
        </div>

        {/* Change Comparison City Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400">COMPARE WITH:</span>
          <select
            value={cityB.id}
            onChange={(e) => setCompareCityId(e.target.value)}
            className="px-3.5 py-2 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs font-mono text-white outline-none focus:border-cyan-400"
          >
            {Object.values(CITIES_DATA).filter(c => c.id !== cityA.id).map((c) => (
              <option key={c.id} value={c.id} className="bg-slate-900">
                {c.name} ({c.country})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Side-by-side Hero Header Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-[#0B1726] border border-cyan-500/40 space-y-2">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-black font-mono text-white uppercase">{cityA.name}</h2>
            <DataTrustBadge status="LIVE" size="sm" />
          </div>
          <p className="text-xs text-slate-400 font-mono">{cityA.country} · {cityA.coordinates}</p>
          <div className="pt-2 text-xs text-slate-300 font-mono">
            Population: {cityA.population} · Density: {cityA.density}
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-[#0B1726] border border-purple-500/40 space-y-2">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-black font-mono text-white uppercase">{cityB.name}</h2>
            <DataTrustBadge status="LIVE" size="sm" />
          </div>
          <p className="text-xs text-slate-400 font-mono">{cityB.country} · {cityB.coordinates}</p>
          <div className="pt-2 text-xs text-slate-300 font-mono">
            Population: {cityB.population} · Density: {cityB.density}
          </div>
        </div>
      </div>

      {/* Comparative Metrics Rows (Section 24) */}
      <div className="space-y-4">
        {metrics.map((m, idx) => {
          const total = (m.rawA + m.rawB) || 1;
          const pctA = Math.round((m.rawA / total) * 100);
          const pctB = 100 - pctA;
          const IconComp = m.icon;

          return (
            <div key={idx} className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <IconComp className="w-4 h-4 text-slate-400" />
                  <span className="text-xs font-bold font-mono text-white uppercase">{m.label}</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">UNIT: {m.unit}</span>
              </div>

              {/* Side-by-side Numerical Values */}
              <div className="flex items-center justify-between text-base font-mono font-bold">
                <span className="text-cyan-400">{m.valA}</span>
                <span className="text-xs text-slate-500 font-normal">VS</span>
                <span className="text-purple-400">{m.valB}</span>
              </div>

              {/* Visual Split Bar */}
              <div className="w-full h-2.5 rounded-full bg-slate-900 border border-[#1E334A] overflow-hidden flex">
                <div
                  className="h-full bg-cyan-400 transition-all duration-300"
                  style={{ width: `${pctA}%` }}
                  title={`${cityA.name}: ${pctA}%`}
                />
                <div
                  className="h-full bg-purple-500 transition-all duration-300"
                  style={{ width: `${pctB}%` }}
                  title={`${cityB.name}: ${pctB}%`}
                />
              </div>

              <div className="flex justify-between text-[10px] font-mono text-slate-400 pt-1">
                <span>{cityA.name} ({pctA}%)</span>
                <span>{cityB.name} ({pctB}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
