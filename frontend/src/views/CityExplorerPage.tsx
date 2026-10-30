import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { CITIES_DATA } from '../data/urbanData';
import { useCities } from '../hooks/useUrbanLens';
import { CityMapCanvas } from '../components/common/CityMapCanvas';
import {
  Compass,
  Search,
  LayoutGrid,
  List,
  Map as MapIcon,
  ArrowRight,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const CityExplorerPage: React.FC = () => {
  const { setCityById, navigate } = useUrban();
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'map'>('grid');
  const [search, setSearch] = useState('');

  // Real backend search
  const { data: searchResults } = useCities({
    q: search || undefined,
    page_size: 24,
  });

  const realCities = searchResults?.data || [];

  const handleSelectCity = (id: string) => {
    setCityById(id);
    navigate('city-detail');
  };

  const seedCities = Object.values(CITIES_DATA);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Compass className="w-4 h-4 text-cyan-400" />
            <span>GLOBAL METROPOLITAN REGISTRY</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            City Explorer
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Search, filter, and inspect verified smart city digital twins across demographics, air quality, transit loads, and living indices.
          </p>
        </div>

        {/* View Mode Switcher: Grid, List, Map */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 p-1 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
              title="Grid View"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
              title="List View"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`p-2 rounded-lg transition-colors ${viewMode === 'map' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
              title="Global Map View"
            >
              <MapIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search 50,250 global cities..."
            className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#0B1726] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-400 outline-none"
          />
        </div>
        <div className="text-xs font-mono text-slate-400">
          {search ? `FOUND ${realCities.length} MATCHING CITIES` : `SHOWING CANONICAL METROPOLITAN HUBS`}
        </div>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {search && realCities.length > 0 ? (
            realCities.map((city) => (
              <div
                key={city.city_id}
                onClick={() => handleSelectCity(city.city_id)}
                className="group rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/50 p-5 transition-all duration-300 hover:shadow-[0_0_25px_rgba(34,211,238,0.15)] hover:-translate-y-1 cursor-pointer flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold font-mono text-white uppercase group-hover:text-cyan-300 transition-colors truncate">
                      {city.name}
                    </h3>
                    <DataTrustBadge status="VERIFIED" size="sm" />
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">{city.country_iso2} · {city.admin_name || 'Metropolitan'}</div>

                  <div className="grid grid-cols-2 gap-2 mt-4 text-xs font-mono">
                    <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[10px] text-slate-400">POPULATION</div>
                      <div className="text-white font-bold mt-0.5 truncate">{city.population ? city.population.toLocaleString() : 'N/A'}</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[10px] text-slate-400">COORDINATES</div>
                      <div className="text-cyan-400 font-bold mt-0.5 truncate">{city.latitude.toFixed(2)}°, {city.longitude.toFixed(2)}°</div>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#1E334A] flex items-center justify-between text-xs font-mono text-cyan-400 group-hover:text-cyan-300">
                  <span>INSPECT DIGITAL TWIN</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))
          ) : (
            seedCities.map((city) => (
              <div
                key={city.id}
                onClick={() => handleSelectCity(city.id)}
                className="group rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/50 p-5 transition-all duration-300 hover:shadow-[0_0_25px_rgba(34,211,238,0.15)] hover:-translate-y-1 cursor-pointer flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold font-mono text-white uppercase group-hover:text-cyan-300 transition-colors">
                      {city.name}
                    </h3>
                    <DataTrustBadge status="LIVE" size="sm" />
                  </div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">{city.country}</div>

                  <div className="grid grid-cols-2 gap-2 mt-4 text-xs font-mono">
                    <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[10px] text-slate-400">POPULATION</div>
                      <div className="text-white font-bold mt-0.5">{city.population}</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[10px] text-slate-400">AQI</div>
                      <div className="text-purple-400 font-bold mt-0.5">AQI {city.aqi}</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[10px] text-slate-400">TEMP</div>
                      <div className="text-cyan-400 font-bold mt-0.5">{city.temperature}°C</div>
                    </div>
                    <div className="p-2.5 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[10px] text-slate-400">TRAFFIC</div>
                      <div className="text-amber-400 font-bold mt-0.5">{city.trafficLoad}%</div>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-[#1E334A] flex items-center justify-between text-xs font-mono text-cyan-400 group-hover:text-cyan-300">
                  <span>INSPECT DIGITAL TWIN</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] overflow-hidden">
          <div className="grid grid-cols-12 p-4 text-[11px] font-mono font-bold text-slate-400 border-b border-[#1E334A] uppercase">
            <div className="col-span-4">City / Country</div>
            <div className="col-span-3 text-right">Population</div>
            <div className="col-span-3 text-right">Coordinates</div>
            <div className="col-span-2 text-right">Status</div>
          </div>
          <div className="divide-y divide-[#1E334A]/50">
            {(search && realCities.length > 0 ? realCities : seedCities).map((c: any) => (
              <div
                key={c.city_id || c.id}
                onClick={() => handleSelectCity(c.city_id || c.id)}
                className="grid grid-cols-12 p-4 text-xs font-mono hover:bg-[#07111F] cursor-pointer transition-colors items-center"
              >
                <div className="col-span-4 font-bold text-white flex items-center gap-2 truncate">
                  <span>{c.name}</span>
                  <span className="text-[10px] text-slate-400 font-normal">({c.country_iso2 || c.countryCode})</span>
                </div>
                <div className="col-span-3 text-right text-slate-300">
                  {c.population?.toLocaleString() || c.population || 'N/A'}
                </div>
                <div className="col-span-3 text-right text-cyan-400 font-mono">
                  {c.latitude ? `${c.latitude.toFixed(2)}°, ${c.longitude.toFixed(2)}°` : c.coordinates}
                </div>
                <div className="col-span-2 text-right">
                  <DataTrustBadge status="VERIFIED" size="sm" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Map View */}
      {viewMode === 'map' && (
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-4 space-y-4">
          <CityMapCanvas heightClass="h-[600px]" />
        </div>
      )}
    </div>
  );
};
