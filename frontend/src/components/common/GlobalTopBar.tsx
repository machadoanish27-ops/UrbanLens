import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUrban } from '../../context/UrbanContext';
import { useOriginDestination } from '../../context/OriginDestinationContext';
import { useCity, useCities } from '../../hooks/useUrbanLens';
import {
  Search,
  Sparkles,
  Bell,
  MapPin,
  ChevronDown,
  Menu,
  ArrowRightLeft
} from 'lucide-react';

interface GlobalTopBarProps {
  onToggleSidebar?: () => void;
}

export const GlobalTopBar: React.FC<GlobalTopBarProps> = ({ onToggleSidebar }) => {
  const {
    activeCityId,
    setActiveCityId,
    toggleAiModal,
    toggleCommandPalette,
    toggleNotifications,
    notifications,
    user
  } = useUrban();

  const { origin, destination, openOriginModal } = useOriginDestination();
  const navigate = useNavigate();

  const { data: cityResp } = useCity(activeCityId);
  const currentCity = cityResp?.data;

  const [isCityDropdownOpen, setIsCityDropdownOpen] = useState(false);
  const [citySearchQuery, setCitySearchQuery] = useState('');

  const { data: searchResults } = useCities({
    q: citySearchQuery.length >= 2 ? citySearchQuery : undefined,
    page_size: 8,
  });

  const popularCities = [
    { id: 'city_1392685764', name: 'Tokyo', country: 'Japan' },
    { id: 'city_1826645935', name: 'London', country: 'United Kingdom' },
    { id: 'city_1356226629', name: 'Mumbai', country: 'India' },
    { id: 'city_1840034016', name: 'New York', country: 'United States' },
    { id: 'city_1250015082', name: 'Paris', country: 'France' },
    { id: 'city_1702341327', name: 'Singapore', country: 'Singapore' },
    { id: 'city_1784736618', name: 'Dubai', country: 'United Arab Emirates' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full h-16 bg-[#030712]/95 backdrop-blur-md border-b border-[#1E334A] px-4 lg:px-6 flex items-center justify-between gap-4">
      {/* Left: Mobile Toggle & Active City Selector */}
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button
            onClick={onToggleSidebar}
            aria-label="Toggle navigation menu"
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#0B1726] border border-transparent hover:border-[#1E334A] transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Active City Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsCityDropdownOpen(!isCityDropdownOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 text-left transition-all duration-200 group"
          >
            <MapPin className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform shrink-0" />
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-xs sm:text-sm font-bold tracking-tight text-white font-mono uppercase truncate">
                  {currentCity?.name || 'Tokyo'}
                </span>
                <span className="text-[9px] font-mono text-emerald-400 font-semibold hidden sm:flex items-center gap-1">
                  <span>●</span> LIVE
                </span>
              </div>
              <div className="text-[10px] text-slate-400 font-mono hidden md:block truncate">
                {currentCity?.country_id?.replace('country_', '') || 'JP'} · {currentCity?.currency?.code || 'JPY'}
              </div>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1 group-hover:text-cyan-400 transition-colors shrink-0" />
          </button>

          {/* City Selection Dropdown */}
          {isCityDropdownOpen && (
            <div
              className="absolute top-full left-0 mt-2 w-72 bg-[#0B1726] border border-[#1E334A] rounded-2xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150"
              onMouseLeave={() => setIsCityDropdownOpen(false)}
            >
              <div className="px-3 py-1.5 text-[10px] font-mono tracking-wider text-slate-400 uppercase border-b border-[#1E334A] mb-2 flex items-center justify-between">
                <span>ACTIVE METROPOLITAN GRID</span>
                <span className="text-cyan-400 font-semibold">50,250 CITIES</span>
              </div>

              {/* Quick Search inside dropdown */}
              <div className="px-2 mb-2">
                <input
                  type="text"
                  value={citySearchQuery}
                  onChange={(e) => setCitySearchQuery(e.target.value)}
                  placeholder="Filter cities..."
                  className="w-full px-2.5 py-1.5 text-xs font-mono rounded-lg bg-[#07111F] border border-[#1E334A] text-white placeholder-slate-500 outline-none focus:border-cyan-400"
                />
              </div>

              <div className="max-h-60 overflow-y-auto space-y-0.5">
                {(searchResults?.data || popularCities).map((c: any) => {
                  const id = c.city_id || c.id;
                  const name = c.name;
                  const country = c.country_id || c.country;
                  const isSelected = id === activeCityId;
                  return (
                    <button
                      key={id}
                      onClick={() => {
                        setActiveCityId(id);
                        setIsCityDropdownOpen(false);
                        setCitySearchQuery('');
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-mono transition-colors ${
                        isSelected
                          ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/30'
                          : 'text-slate-300 hover:bg-[#1E334A]/50'
                      }`}
                    >
                      <div className="text-left truncate">
                        <div className="font-semibold text-white">{name}</div>
                        <div className="text-[10px] text-slate-400">{country}</div>
                      </div>
                      {isSelected && <span className="text-[10px] text-cyan-400 font-bold">ACTIVE</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Relocation Context Pill (Origin -> Destination Currency) */}
        <button
          onClick={openOriginModal}
          className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-300 transition-colors group"
          title="Configure Relocation Origin & Target Destination"
        >
          <ArrowRightLeft className="w-3.5 h-3.5 text-cyan-400 group-hover:rotate-180 transition-transform duration-300" />
          <span className="text-slate-400">FX:</span>
          <span className="font-bold text-white">{origin.currency_code}</span>
          <span className="text-cyan-400">→</span>
          <span className="font-bold text-white">{currentCity?.currency?.code || destination?.currency_code || 'JPY'}</span>
        </button>
      </div>

      {/* Center: Global Search Trigger (Cmd + K) */}
      <button
        onClick={() => toggleCommandPalette(true)}
        className="flex-1 max-w-md hidden sm:flex items-center justify-between px-3.5 py-1.5 rounded-xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-400 transition-all duration-200 group"
      >
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-400 group-hover:text-cyan-400 transition-colors" />
          <span className="truncate">Search cities, telemetry, RAG knowledge...</span>
        </div>
        <kbd className="px-1.5 py-0.5 rounded bg-[#07111F] border border-[#1E334A] text-[10px] text-slate-400 font-mono">
          ⌘K
        </kbd>
      </button>

      {/* Right Action Icons: Ask AI, Notifications, User */}
      <div className="flex items-center gap-2">
        {/* Quick Ask AI Trigger */}
        <button
          onClick={() => toggleAiModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-500/20 via-blue-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 border border-cyan-500/40 text-xs font-mono font-semibold text-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.15)] transition-all"
          title="Open AI Intelligence Assistant"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin-slow" />
          <span className="hidden sm:inline">ASK AI</span>
        </button>

        {/* Notifications Bell */}
        <button
          onClick={() => toggleNotifications(true)}
          className="relative p-2 rounded-xl text-slate-400 hover:text-white hover:bg-[#0B1726] border border-transparent hover:border-[#1E334A] transition-colors"
          title="System notifications"
        >
          <Bell className="w-4 h-4" />
          {notifications.length > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          )}
        </button>

        {/* User Profile Avatar */}
        <div
          onClick={() => navigate('/app/settings')}
          className="flex items-center gap-2 pl-2 border-l border-[#1E334A] cursor-pointer group"
          title={`${user.name} (${user.role})`}
        >
          <img
            src={user.avatarUrl}
            alt={user.name}
            className="w-8 h-8 rounded-lg object-cover border border-[#1E334A] group-hover:border-cyan-400 transition-colors"
            onError={(e) => {
              // Fallback on missing image
              (e.currentTarget as HTMLElement).style.display = 'none';
            }}
          />
          <div className="hidden xl:block text-left">
            <div className="text-xs font-mono font-bold text-white group-hover:text-cyan-300 transition-colors">
              {user.name.split(' ')[0]}
            </div>
            <div className="text-[10px] font-mono text-slate-400 truncate max-w-[100px]">
              {user.role.split(' ')[0]}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
