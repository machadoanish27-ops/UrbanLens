import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { CITIES_DATA } from '../data/urbanData';
import { Search, ArrowRight } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const CityOnboarding: React.FC = () => {
  const { setCityById, navigate } = useUrban();
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCityId, setHoveredCityId] = useState<string | null>(null);

  const citiesList = Object.values(CITIES_DATA).filter((c) =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.country.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectCity = (id: string) => {
    setCityById(id);
    // After initialization delay in context, navigate to dashboard
    setTimeout(() => {
      navigate('dashboard');
    }, 1300);
  };

  return (
    <div className="min-h-screen bg-[#030712] text-white p-6 sm:p-12 relative overflow-hidden font-sans">
      <div className="absolute inset-0 bg-spatial-grid opacity-30 pointer-events-none" />

      <div className="max-w-6xl mx-auto space-y-8 relative z-10">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[#1E334A] pb-6">
          <div>
            <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-1.5">
              <span>● SYSTEM OPERATIONAL</span>
              <span>·</span>
              <span>RESTRICTED ACCESS</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-black font-display uppercase tracking-tight text-white mt-2">
              CHOOSE YOUR CITY
            </h1>
            <p className="text-sm text-slate-300 font-sans mt-1">
              Select an urban intelligence grid to establish live telemetry connection and digital twin telemetry.
            </p>
          </div>

          {/* City Search Bar */}
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter by city or country..."
              className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#0B1726] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-400 outline-none"
            />
          </div>
        </div>

        {/* Featured Cities Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {citiesList.map((city) => {
            const isHovered = hoveredCityId === city.id;

            return (
              <div
                key={city.id}
                onMouseEnter={() => setHoveredCityId(city.id)}
                onMouseLeave={() => setHoveredCityId(null)}
                onClick={() => handleSelectCity(city.id)}
                className="group relative rounded-2xl bg-[#0B1726]/80 backdrop-blur-md border border-[#1E334A] hover:border-cyan-500/60 p-5 cursor-pointer transition-all duration-300 hover:shadow-[0_0_30px_rgba(34,211,238,0.2)] hover:-translate-y-1 flex flex-col justify-between overflow-hidden"
              >
                {/* Luminous Top Accent on hover */}
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-blue-500 opacity-0 group-hover:opacity-100 transition-opacity" />

                <div>
                  {/* Card Header: City, Country & Status */}
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div>
                      <h3 className="text-lg font-bold font-mono text-white uppercase group-hover:text-cyan-300 transition-colors">
                        {city.name}
                      </h3>
                      <p className="text-xs text-slate-400 font-mono">
                        {city.country}
                      </p>
                    </div>
                    <DataTrustBadge status="LIVE" size="sm" />
                  </div>

                  {/* Stylized Mini Map Vector */}
                  <div className="w-full h-28 rounded-xl bg-[#07111F] border border-[#1E334A] overflow-hidden relative mb-4 flex items-center justify-center">
                    <div className="absolute inset-0 bg-spatial-dots opacity-40" />

                    {/* Abstract city transit nodes */}
                    <svg viewBox="0 0 200 100" className="w-full h-full">
                      <path
                        d="M 20 50 Q 80 20 120 60 T 180 40"
                        fill="none"
                        stroke={isHovered ? '#22D3EE' : '#1E334A'}
                        strokeWidth="2"
                        className="transition-colors duration-300"
                      />
                      <path
                        d="M 40 80 Q 90 90 140 30"
                        fill="none"
                        stroke={isHovered ? '#3B82F6' : '#1E334A'}
                        strokeWidth="1.5"
                        strokeDasharray="4,4"
                      />
                      <circle cx="120" cy="60" r="5" fill="#22D3EE" className="animate-pulse" />
                      <circle cx="60" cy="35" r="3.5" fill="#8B5CF6" />
                      <circle cx="160" cy="45" r="4" fill="#10B981" />
                    </svg>

                    <div className="absolute bottom-1.5 left-2 text-[9px] font-mono text-slate-400">
                      GRID {city.coordinates.split(',')[0]}
                    </div>
                  </div>

                  {/* Metrics strip */}
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-2 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[9px] font-mono text-slate-400">POPULATION</div>
                      <div className="text-xs font-bold font-mono text-white mt-0.5 truncate">
                        {city.population.split(',')[0]}M
                      </div>
                    </div>

                    <div className="p-2 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[9px] font-mono text-slate-400">TEMP</div>
                      <div className="text-xs font-bold font-mono text-cyan-400 mt-0.5">
                        {city.temperature}°C
                      </div>
                    </div>

                    <div className="p-2 rounded-lg bg-[#07111F] border border-[#1E334A]">
                      <div className="text-[9px] font-mono text-slate-400">AQI</div>
                      <div className="text-xs font-bold font-mono text-purple-400 mt-0.5">
                        {city.aqi}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Intelligence revealed on hover */}
                <div className={`mt-4 pt-3 border-t border-[#1E334A] transition-all duration-300 ${isHovered ? 'opacity-100 max-h-20' : 'opacity-80 max-h-12'}`}>
                  <div className="text-[10px] font-mono text-slate-300 flex items-center justify-between">
                    <span>{city.zones.length} ZONES ACTIVE</span>
                    <span className="text-cyan-400 flex items-center gap-1 font-semibold group-hover:translate-x-1 transition-transform">
                      INITIALIZE <ArrowRight className="w-3 h-3" />
                    </span>
                  </div>
                  {isHovered && (
                    <div className="text-[10px] font-sans text-slate-400 mt-1 line-clamp-1">
                      {city.zones[0]?.aiSignal}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
