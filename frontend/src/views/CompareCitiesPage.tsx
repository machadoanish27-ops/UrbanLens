import React from 'react';
import { useUrban } from '../context/UrbanContext';
import { CITIES_DATA } from '../data/urbanData';
import { Scale, Users, Wind, Thermometer, Car, Coins, TrendingUp } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const CompareCitiesPage: React.FC = () => {
  const { currentCity, compareCityId, setCompareCityId } = useUrban();

  const cityA = currentCity;
  const rawCityBKey = compareCityId.toLowerCase();
  const fallbackKey = (cityA.name.toLowerCase() === 'tokyo' || cityA.id.includes('1392685764')) ? 'london' : 'tokyo';
  const effectiveCityBKey = (rawCityBKey === cityA.name.toLowerCase() || rawCityBKey === cityA.id.toLowerCase())
    ? fallbackKey
    : (CITIES_DATA[rawCityBKey] ? rawCityBKey : fallbackKey);
  const cityB = CITIES_DATA[effectiveCityBKey] || CITIES_DATA[fallbackKey];

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
            {Object.values(CITIES_DATA).filter(c => c.name.toLowerCase() !== cityA.name.toLowerCase()).map((c) => (
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

      {/* Telemetry Matrix Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          const aIsBetter = m.lowerIsBetter ? m.rawA < m.rawB : m.rawA > m.rawB;
          const bIsBetter = m.lowerIsBetter ? m.rawB < m.rawA : m.rawB > m.rawA;

          return (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3"
            >
              <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-cyan-400" />
                  <span className="font-bold text-white uppercase">{m.label}</span>
                </div>
                <span className="text-[10px] text-slate-400">{m.unit}</span>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-[#1E334A]">
                {/* Metric A */}
                <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A]">
                  <div className="text-[10px] font-mono text-cyan-400 font-bold uppercase truncate">
                    {cityA.name}
                  </div>
                  <div className="text-lg font-black font-mono text-white mt-0.5 truncate">
                    {m.valA}
                  </div>
                  {aIsBetter && (
                    <span className="text-[9px] font-mono text-emerald-400 font-bold block mt-1">
                      OPTIMAL VALUE
                    </span>
                  )}
                </div>

                {/* Metric B */}
                <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A]">
                  <div className="text-[10px] font-mono text-purple-400 font-bold uppercase truncate">
                    {cityB.name}
                  </div>
                  <div className="text-lg font-black font-mono text-white mt-0.5 truncate">
                    {m.valB}
                  </div>
                  {bIsBetter && (
                    <span className="text-[9px] font-mono text-emerald-400 font-bold block mt-1">
                      OPTIMAL VALUE
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
