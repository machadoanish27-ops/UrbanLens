import React, { useState } from 'react';
import { X, MapPin, Globe, Check, Search } from 'lucide-react';
import { useOriginDestination, type OriginLocation } from '../context/OriginDestinationContext';
import { useCities } from '../hooks/useUrbanLens';

const POPULAR_ORIGIN_CITIES = [
  {
    city_id: 'city_1356226629',
    city_name: 'Mumbai',
    country_id: 'country_IN',
    country_name: 'India',
    country_iso2: 'IN',
    currency_code: 'INR',
    currency_symbol: '₹',
    currency_name: 'Indian Rupee',
  },
  {
    city_id: 'city_1356872604',
    city_name: 'Delhi',
    country_id: 'country_IN',
    country_name: 'India',
    country_iso2: 'IN',
    currency_code: 'INR',
    currency_symbol: '₹',
    currency_name: 'Indian Rupee',
  },
  {
    city_id: 'city_1356060597',
    city_name: 'Bengaluru',
    country_id: 'country_IN',
    country_name: 'India',
    country_iso2: 'IN',
    currency_code: 'INR',
    currency_symbol: '₹',
    currency_name: 'Indian Rupee',
  },
  {
    city_id: 'city_1826645935',
    city_name: 'London',
    country_id: 'country_GB',
    country_name: 'United Kingdom',
    country_iso2: 'GB',
    currency_code: 'GBP',
    currency_symbol: '£',
    currency_name: 'British Pound',
  },
  {
    city_id: 'city_1840034016',
    city_name: 'New York',
    country_id: 'country_US',
    country_name: 'United States',
    country_iso2: 'US',
    currency_code: 'USD',
    currency_symbol: '$',
    currency_name: 'US Dollar',
  },
  {
    city_id: 'city_1250015082',
    city_name: 'Paris',
    country_id: 'country_FR',
    country_name: 'France',
    country_iso2: 'FR',
    currency_code: 'EUR',
    currency_symbol: '€',
    currency_name: 'Euro',
  },
  {
    city_id: 'city_1702341327',
    city_name: 'Singapore',
    country_id: 'country_SG',
    country_name: 'Singapore',
    country_iso2: 'SG',
    currency_code: 'SGD',
    currency_symbol: 'S$',
    currency_name: 'Singapore Dollar',
  },
  {
    city_id: 'city_1784736618',
    city_name: 'Dubai',
    country_id: 'country_AE',
    country_name: 'United Arab Emirates',
    country_iso2: 'AE',
    currency_code: 'AED',
    currency_symbol: 'د.إ',
    currency_name: 'UAE Dirham',
  },
];

export const OriginSelectorModal: React.FC = () => {
  const { origin, setOrigin, isOriginModalOpen, closeOriginModal } = useOriginDestination();
  const [searchTerm, setSearchTerm] = useState('');

  const { data: searchResults, isLoading: isSearching } = useCities({
    q: searchTerm.trim() || undefined,
    page_size: 8,
  });

  if (!isOriginModalOpen) return null;

  const handleSelectCity = (c: any) => {
    const iso2 = c.country_iso2 || 'US';
    // Match currency
    const popularMatch = POPULAR_ORIGIN_CITIES.find((p) => p.city_id === c.city_id);
    const currCode = popularMatch?.currency_code || (iso2 === 'IN' ? 'INR' : iso2 === 'GB' ? 'GBP' : iso2 === 'JP' ? 'JPY' : iso2 === 'FR' || iso2 === 'DE' ? 'EUR' : 'USD');
    const currSym = popularMatch?.currency_symbol || (currCode === 'INR' ? '₹' : currCode === 'GBP' ? '£' : currCode === 'JPY' ? '¥' : currCode === 'EUR' ? '€' : '$');
    const currName = popularMatch?.currency_name || (currCode === 'INR' ? 'Indian Rupee' : 'US Dollar');

    const newOrigin: OriginLocation = {
      country_id: c.country_id || `country_${iso2}`,
      country_name: c.country_name || iso2,
      country_iso2: iso2,
      city_id: c.city_id,
      city_name: c.name || c.city_name,
      currency_code: currCode,
      currency_symbol: currSym,
      currency_name: currName,
      source: 'User Selection (Persisted Profile)',
    };

    setOrigin(newOrigin);
    closeOriginModal();
  };

  const citiesList = searchTerm.trim()
    ? searchResults?.data || []
    : POPULAR_ORIGIN_CITIES;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg glass-panel p-6 rounded-2xl border border-slate-700/80 shadow-2xl relative bg-slate-900/95">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Globe className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Select Origin Profile</h2>
              <p className="text-xs text-slate-400">Where are you relocating from?</p>
            </div>
          </div>
          <button
            onClick={closeOriginModal}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Current Origin Badge */}
        <div className="my-4 p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-indigo-300">Active Origin</span>
            <div className="text-sm font-bold text-white flex items-center gap-1.5 mt-0.5">
              <MapPin className="w-3.5 h-3.5 text-indigo-400" />
              <span>{origin.city_name}, {origin.country_name}</span>
              <span className="text-xs text-indigo-300 font-mono">({origin.currency_code} {origin.currency_symbol})</span>
            </div>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-medium border border-indigo-500/30">
            Selected
          </span>
        </div>

        {/* Search Input */}
        <div className="relative mb-4">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500 pointer-events-none" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search canonical cities worldwide..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-slate-950/90 border border-slate-800 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            autoFocus
          />
        </div>

        {/* Results List */}
        <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-1 mb-1">
            {searchTerm.trim() ? 'Search Results' : 'Suggested Hubs'}
          </p>

          {isSearching && (
            <div className="py-6 text-center text-xs text-slate-500">Searching canonical registry...</div>
          )}

          {!isSearching && citiesList.length === 0 && (
            <div className="py-6 text-center text-xs text-slate-500">No canonical cities found matching query.</div>
          )}

          {!isSearching &&
            citiesList.map((c: any) => {
              const isSelected = c.city_id === origin.city_id;
              const cityName = c.name || c.city_name;
              const countryName = c.country_name || c.country_iso2;
              const currCode = c.currency_code || (c.country_iso2 === 'IN' ? 'INR' : c.country_iso2 === 'GB' ? 'GBP' : c.country_iso2 === 'JP' ? 'JPY' : 'USD');
              const currSym = c.currency_symbol || (currCode === 'INR' ? '₹' : currCode === 'GBP' ? '£' : currCode === 'JPY' ? '¥' : '$');

              return (
                <button
                  key={c.city_id}
                  onClick={() => handleSelectCity(c)}
                  className={`w-full flex items-center justify-between p-2.5 rounded-xl text-left text-xs transition-colors ${
                    isSelected
                      ? 'bg-indigo-600/20 border border-indigo-500/40 text-white'
                      : 'hover:bg-slate-800/60 text-slate-300 hover:text-white border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <div>
                      <span className="font-semibold text-white">{cityName}</span>
                      <span className="text-slate-400 ml-1.5">{countryName}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-[11px] text-indigo-300">
                      {currCode} {currSym}
                    </span>
                    {isSelected && <Check className="w-4 h-4 text-emerald-400 shrink-0" />}
                  </div>
                </button>
              );
            })}
        </div>

        {/* Provenance Footer */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Source: User Selection (Persisted in browser)</span>
          <button
            onClick={closeOriginModal}
            className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
