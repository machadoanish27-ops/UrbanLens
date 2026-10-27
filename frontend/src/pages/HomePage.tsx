import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Search,
  Sparkles,
  MapPin,
  Users,
  Compass,
  ArrowRight,
  Shield,
  Layers,
  Thermometer,
  Wind,
  Coins,
  GraduationCap,
  Bus,
} from 'lucide-react';
import { useCities } from '../hooks/useUrbanLens';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

const SUGGESTED_PROMPTS = [
  {
    query: 'What is the current air quality and weather in Tokyo?',
    cityId: 'city_1392685764',
    category: 'Environment',
  },
  {
    query: 'Is London or Paris more affordable for university students?',
    cityId: 'city_1826645935',
    category: 'Education & Cost',
  },
  {
    query: 'Analyze the public transit and population density of Mumbai.',
    cityId: 'city_1356226629',
    category: 'Mobility',
  },
  {
    query: 'What are the key economic and living factors in New York?',
    cityId: 'city_1840034016',
    category: 'Overview',
  },
];

const FEATURED_CITIES = [
  { id: 'city_1392685764', name: 'Tokyo', country: 'Japan', iso2: 'JP', pop: 37732000, tag: 'Megacity' },
  { id: 'city_1356226629', name: 'Mumbai', country: 'India', iso2: 'IN', pop: 20961472, tag: 'Economic Hub' },
  { id: 'city_1826645935', name: 'London', country: 'United Kingdom', iso2: 'GB', pop: 9540576, tag: 'Global Capital' },
  { id: 'city_1250015082', name: 'Paris', country: 'France', iso2: 'FR', pop: 2161000, tag: 'Cultural Center' },
  { id: 'city_1840034016', name: 'New York', country: 'United States', iso2: 'US', pop: 8804190, tag: 'Financial Center' },
  { id: 'city_1276451290', name: 'Berlin', country: 'Germany', iso2: 'DE', pop: 3850809, tag: 'Innovation Hub' },
];

export const HomePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const navigate = useNavigate();

  const { data: citiesData, isLoading: isSearching, error: searchError } = useCities({
    q: searchQuery.trim() || undefined,
    page_size: 10,
  });

  const cities = citiesData?.data || [];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setSearchParams({ q: searchQuery.trim() });
    }
  };

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-12 md:py-16 relative">
        <div className="absolute inset-0 -top-20 -z-10 flex items-center justify-center">
          <div className="w-[600px] h-[300px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-medium mb-6">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Next-Generation Multi-Agent Urban Intelligence</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight md:leading-tight">
          Authoritative City Insights,{' '}
          <span className="bg-gradient-to-r from-indigo-400 via-cyan-400 to-teal-300 bg-clip-text text-transparent">
            Strictly Grounded
          </span>
        </h1>

        <p className="text-slate-400 text-base md:text-lg max-w-2xl mx-auto mt-4 leading-relaxed">
          Explore real-time weather, air quality, transit, cost of living, and university rankings across global cities. Synthesized with zero hallucinations via Groq LLM reasoning.
        </p>

        {/* Global City Search Form */}
        <div className="max-w-2xl mx-auto mt-8">
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="w-5 h-5 absolute left-4 top-3.5 text-slate-400 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (!e.target.value) {
                  setSearchParams({});
                }
              }}
              placeholder="Search by city name (e.g. Tokyo, Mumbai, London, Paris)..."
              className="w-full pl-12 pr-28 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-white placeholder:text-slate-500 text-base shadow-2xl focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 transition-all"
            />
            <button
              type="submit"
              className="absolute right-2 top-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl transition-all shadow-md shadow-indigo-600/30 flex items-center gap-1.5"
            >
              <span>Search</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Search Results Dropdown/List when active */}
          {searchQuery.trim().length > 0 && (
            <div className="mt-3 p-2 rounded-2xl glass-panel border border-slate-800 text-left divide-y divide-slate-800/80 shadow-2xl">
              {isSearching ? (
                <div className="p-4 text-center text-xs text-slate-400">
                  <LoadingSkeleton count={2} height="h-12" />
                </div>
              ) : searchError ? (
                <div className="p-4 text-center text-xs text-rose-400">
                  Could not load search results. Please check your backend connection.
                </div>
              ) : cities.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500">
                  No cities found matching "{searchQuery}".
                </div>
              ) : (
                cities.map((city) => (
                  <div
                    key={city.city_id}
                    onClick={() => navigate(`/city/${encodeURIComponent(city.city_id)}`)}
                    className="p-3 hover:bg-slate-800/70 rounded-xl cursor-pointer flex items-center justify-between transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                        <MapPin className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors">
                          {city.name}
                          <span className="ml-2 text-xs font-normal text-slate-400">
                            {city.country_iso2}
                          </span>
                        </div>
                        <div className="text-xs text-slate-500">
                          {city.admin_name || city.country_id} • Pop: {city.population ? city.population.toLocaleString() : 'N/A'}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                        View Intelligence &rarr;
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </section>

      {/* Suggested Prompt Chips */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <h2 className="text-lg font-bold text-slate-200">
              Ask AI Intelligence with Grounded Evidence
            </h2>
          </div>
          <Link
            to="/ask"
            className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            <span>Explore all queries</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {SUGGESTED_PROMPTS.map((prompt, idx) => (
            <div
              key={idx}
              onClick={() =>
                navigate(`/ask?q=${encodeURIComponent(prompt.query)}&cityId=${prompt.cityId}`)
              }
              className="glass-panel glass-panel-hover p-4 rounded-xl cursor-pointer flex flex-col justify-between border border-slate-800 text-left group"
            >
              <div>
                <span className="inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 mb-2">
                  {prompt.category}
                </span>
                <p className="text-xs text-slate-300 font-medium group-hover:text-white transition-colors leading-relaxed">
                  "{prompt.query}"
                </p>
              </div>
              <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
                <span>Grounded with Groq</span>
                <ArrowRight className="w-3.5 h-3.5 text-indigo-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Featured Cities Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Compass className="w-4 h-4 text-cyan-400" />
            <h2 className="text-lg font-bold text-slate-200">
              Featured Global Metropolitan Hubs
            </h2>
          </div>
          <span className="text-xs text-slate-500">Live API Ready</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURED_CITIES.map((city) => (
            <div
              key={city.id}
              className="glass-panel p-5 rounded-2xl border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {city.tag}
                  </span>
                  <span className="text-xs font-mono font-medium text-indigo-400">
                    {city.iso2}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-white group-hover:text-indigo-300 transition-colors">
                  {city.name}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">{city.country}</p>

                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center gap-4 text-xs text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-slate-500" />
                    <span>{city.pop.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-500" />
                    <span className="font-mono text-[11px]">{city.id}</span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-800/60 flex items-center gap-2">
                <Link
                  to={`/city/${city.id}`}
                  className="flex-1 py-2 px-3 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold text-center transition-all flex items-center justify-center gap-1.5"
                >
                  <Compass className="w-3.5 h-3.5" />
                  <span>Inspect City</span>
                </Link>
                <Link
                  to={`/ask?cityId=${city.id}`}
                  className="py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold transition-all flex items-center justify-center gap-1"
                  title="Ask AI about this city"
                >
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Intelligence Domains Architecture Ribbon */}
      <section className="glass-panel p-8 rounded-2xl border border-slate-800">
        <div className="text-center max-w-2xl mx-auto mb-8">
          <h2 className="text-xl font-bold text-white">7 Autonomous Domain Intelligence Agents</h2>
          <p className="text-xs text-slate-400 mt-2">
            Every UrbanLens assessment is verified against multi-provider real-time signals and dense vector knowledge.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4 text-center">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <Thermometer className="w-5 h-5 text-indigo-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Weather</span>
            <span className="text-[10px] text-slate-500 mt-0.5">Open-Meteo</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <Wind className="w-5 h-5 text-teal-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Air Quality</span>
            <span className="text-[10px] text-slate-500 mt-0.5">OpenAQ & WHO</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <Coins className="w-5 h-5 text-amber-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Cost Index</span>
            <span className="text-[10px] text-slate-500 mt-0.5">Numbeo/Atlas</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <Bus className="w-5 h-5 text-blue-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Transit</span>
            <span className="text-[10px] text-slate-500 mt-0.5">GTFS / Overpass</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <GraduationCap className="w-5 h-5 text-purple-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Universities</span>
            <span className="text-[10px] text-slate-500 mt-0.5">QS & CWUR</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <Shield className="w-5 h-5 text-emerald-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Safety</span>
            <span className="text-[10px] text-slate-500 mt-0.5">Gov & Indices</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 flex flex-col items-center">
            <Layers className="w-5 h-5 text-rose-400 mb-2" />
            <span className="text-xs font-bold text-slate-200">Economy</span>
            <span className="text-[10px] text-slate-500 mt-0.5">Census Data</span>
          </div>
        </div>
      </section>
    </div>
  );
};
