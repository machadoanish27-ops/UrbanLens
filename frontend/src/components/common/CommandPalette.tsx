import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUrban } from '../../context/UrbanContext';
import { useCities } from '../../hooks/useUrbanLens';
import {
  Search,
  MapPin,
  Compass,
  Scale,
  Sparkles,
  CloudSun,
  Wind,
  Car,
  Coins,
  GraduationCap,
  HeartPulse,
  DollarSign,
  BookOpen,
  Settings,
  X,
  ArrowRight
} from 'lucide-react';

export const CommandPalette: React.FC = () => {
  const { isCommandPaletteOpen, toggleCommandPalette, setActiveCityId } = useUrban();
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const { data: searchResults, isLoading } = useCities({
    q: query.trim().length >= 2 ? query.trim() : undefined,
    page_size: 6,
  });

  const quickNavItems = [
    { label: 'Dashboard Overview', path: '/app', icon: Compass, category: 'Navigation' },
    { label: 'Global Map View', path: '/app/map', icon: Compass, category: 'Navigation' },
    { label: 'Global City Explorer', path: '/app/explore', icon: Compass, category: 'Navigation' },
    { label: 'Cross-Metropolitan Compare', path: '/app/compare', icon: Scale, category: 'Intelligence' },
    { label: 'Ask AI Multi-Agent Intelligence', path: '/app/ask', icon: Sparkles, category: 'Intelligence' },
    { label: 'Weather & Climate Observables', path: '/app/weather', icon: CloudSun, category: 'Telemetry' },
    { label: 'Air Quality & Environmental Index', path: '/app/air-quality', icon: Wind, category: 'Telemetry' },
    { label: 'Mobility & Public Transit Feed', path: '/app/mobility', icon: Car, category: 'Infrastructure' },
    { label: 'Cost of Living & Purchasing Power', path: '/app/cost', icon: Coins, category: 'Economics' },
    { label: 'Education & Verified Universities', path: '/app/education', icon: GraduationCap, category: 'Institutions' },
    { label: 'Healthcare & Emergency Facilities', path: '/app/healthcare', icon: HeartPulse, category: 'Institutions' },
    { label: 'Global Currency & ECB Exchange Rates', path: '/app/currency', icon: DollarSign, category: 'Economics' },
    { label: 'Authoritative RAG Knowledge Center', path: '/app/knowledge', icon: BookOpen, category: 'Research' },
    { label: 'Platform & Relocation Settings', path: '/app/settings', icon: Settings, category: 'System' },
  ];

  const filteredNav = quickNavItems.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase()) ||
    item.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelectNav = (path: string) => {
    navigate(path);
    toggleCommandPalette(false);
    setQuery('');
  };

  const handleSelectCity = (cityId: string) => {
    setActiveCityId(cityId);
    navigate(`/app/city/${cityId}`);
    toggleCommandPalette(false);
    setQuery('');
  };

  if (!isCommandPaletteOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-start justify-center pt-16 sm:pt-24 px-4 animate-in fade-in duration-150"
      onClick={() => toggleCommandPalette(false)}
    >
      <div
        className="w-full max-w-2xl bg-[#0B1726] border border-[#1E334A] rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="relative flex items-center px-4 py-3.5 border-b border-[#1E334A]">
          <Search className="w-5 h-5 text-cyan-400 shrink-0 mr-3" />
          <input
            type="text"
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a city name (e.g., Tokyo, London, Paris) or command..."
            className="w-full bg-transparent text-sm sm:text-base font-mono text-white placeholder-slate-500 outline-none"
          />
          <button
            onClick={() => toggleCommandPalette(false)}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E334A] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Results Container */}
        <div className="max-h-[60vh] overflow-y-auto p-3 space-y-4 scrollbar-thin">
          {/* City Search Results */}
          {query.trim().length >= 2 && (
            <div>
              <div className="px-3 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center justify-between">
                <span>CITIES MATCHING "{query.toUpperCase()}"</span>
                {isLoading && <span className="text-cyan-400">SEARCHING...</span>}
              </div>
              {searchResults?.data && searchResults.data.length > 0 ? (
                <div className="space-y-1">
                  {searchResults.data.map((city) => (
                    <button
                      key={city.city_id}
                      onClick={() => handleSelectCity(city.city_id)}
                      className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-[#07111F] hover:bg-[#1E334A]/60 border border-[#1E334A] hover:border-cyan-500/40 text-left transition-all group"
                    >
                      <div className="flex items-center gap-3">
                        <MapPin className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                        <div>
                          <div className="text-xs font-mono font-bold text-white group-hover:text-cyan-300">
                            {city.name}
                          </div>
                          <div className="text-[10px] font-mono text-slate-400">
                            {city.country_iso2} · Pop: {city.population ? Number(city.population).toLocaleString() : 'N/A'}
                          </div>
                        </div>
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
                    </button>
                  ))}
                </div>
              ) : !isLoading ? (
                <div className="px-3 py-2 text-xs font-mono text-slate-500">
                  No cities found matching "{query}".
                </div>
              ) : null}
            </div>
          )}

          {/* Quick Navigation Commands */}
          <div>
            <div className="px-3 text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1.5">
              APPLICATION COMMANDS & DOMAINS
            </div>
            <div className="space-y-1">
              {filteredNav.slice(0, 8).map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.path}
                    onClick={() => handleSelectNav(item.path)}
                    className="w-full flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-mono text-slate-300 hover:text-white hover:bg-[#07111F] transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" />
                      <span>{item.label}</span>
                    </div>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                      {item.category}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="px-4 py-2 bg-[#07111F] border-t border-[#1E334A] flex items-center justify-between text-[10px] font-mono text-slate-500">
          <span>Press ESC to close</span>
          <span>UrbanLens Operating System</span>
        </div>
      </div>
    </div>
  );
};
