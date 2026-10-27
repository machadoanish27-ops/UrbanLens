import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Columns2,
  Sparkles,
  ArrowRight,
  ArrowLeftRight,
  MapPin,
  Thermometer,
  Wind,
  Coins,
  GraduationCap,
  Bus,
  ShieldCheck,
  Layers,
  Users,
} from 'lucide-react';
import {
  useCities,
  useCity,
  useCityWeather,
  useCityAirQuality,
  useCityCost,
  useCityUniversities,
  useCityTransit,
  useCityPlaces,
  useCityIntelligence,
} from '../hooks/useUrbanLens';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

const COMPARISON_PRESETS = [
  { c1: 'city_1392685764', c2: 'city_1826645935', label: 'Tokyo vs London' },
  { c1: 'city_1356226629', c2: 'city_1840034016', label: 'Mumbai vs New York' },
  { c1: 'city_1250015082', c2: 'city_1276451290', label: 'Paris vs Berlin' },
];

export const ComparePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const city1Id = searchParams.get('city1') || 'city_1392685764';
  const city2Id = searchParams.get('city2') || 'city_1826645935';

  const [selected1, setSelected1] = useState(city1Id);
  const [selected2, setSelected2] = useState(city2Id);

  const { data: citiesData } = useCities({ page_size: 50 });
  const cities = citiesData?.data || [];

  // City 1 data queries
  const { data: c1Detail, isLoading: c1Loading } = useCity(selected1);
  const { data: c1Weather } = useCityWeather(selected1);
  const { data: c1Aqi } = useCityAirQuality(selected1);
  const { data: c1Cost } = useCityCost(selected1);
  const { data: c1Unis } = useCityUniversities(selected1);
  const { data: c1Transit } = useCityTransit(selected1);
  const { data: c1Intel } = useCityIntelligence(selected1);
  const { data: c1Places } = useCityPlaces({
    lat: c1Detail?.data?.latitude ?? 0,
    lon: c1Detail?.data?.longitude ?? 0,
    category: 'hospital',
    radius: 4000,
    limit: 10,
  });

  // City 2 data queries
  const { data: c2Detail, isLoading: c2Loading } = useCity(selected2);
  const { data: c2Weather } = useCityWeather(selected2);
  const { data: c2Aqi } = useCityAirQuality(selected2);
  const { data: c2Cost } = useCityCost(selected2);
  const { data: c2Unis } = useCityUniversities(selected2);
  const { data: c2Transit } = useCityTransit(selected2);
  const { data: c2Intel } = useCityIntelligence(selected2);
  const { data: c2Places } = useCityPlaces({
    lat: c2Detail?.data?.latitude ?? 0,
    lon: c2Detail?.data?.longitude ?? 0,
    category: 'hospital',
    radius: 4000,
    limit: 10,
  });

  const handleCity1Change = (id: string) => {
    setSelected1(id);
    setSearchParams({ city1: id, city2: selected2 });
  };

  const handleCity2Change = (id: string) => {
    setSelected2(id);
    setSearchParams({ city1: selected1, city2: id });
  };

  const handleSwapCities = () => {
    const temp = selected1;
    setSelected1(selected2);
    setSelected2(temp);
    setSearchParams({ city1: selected2, city2: temp });
  };

  const handlePresetSelect = (c1: string, c2: string) => {
    setSelected1(c1);
    setSelected2(c2);
    setSearchParams({ city1: c1, city2: c2 });
  };

  const handleAskAiToCompare = () => {
    const c1Name = c1Detail?.data?.name || selected1;
    const c2Name = c2Detail?.data?.name || selected2;
    const prompt = `Compare ${c1Name} and ${c2Name} in terms of live weather, air quality, cost of living, transit, healthcare, and universities. Which is better suited for relocation and career opportunities?`;
    navigate(`/ask?q=${encodeURIComponent(prompt)}&cityId=${selected1}`);
  };

  const c1 = c1Detail?.data;
  const c2 = c2Detail?.data;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
          <Columns2 className="w-3.5 h-3.5" />
          <span>Side-by-Side Metropolitan Benchmarking</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Compare Global Cities
        </h1>
        <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
          Compare real demographics, live weather, air quality sensors, universities, and cost indices head-to-head without fabricated scoring.
        </p>

        {/* Quick Presets */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
          <span className="text-xs text-slate-500">Popular comparisons:</span>
          {COMPARISON_PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handlePresetSelect(p.c1, p.c2)}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-indigo-300 transition-colors"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 flex flex-col md:flex-row items-center gap-4 shadow-xl">
        {/* City 1 Selector */}
        <div className="flex-1 w-full">
          <label htmlFor="city1-select" className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            City Benchmark A
          </label>
          <select
            id="city1-select"
            value={selected1}
            onChange={(e) => handleCity1Change(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm font-semibold text-white focus:outline-none focus:border-indigo-500 focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            {cities.map((city) => (
              <option key={city.city_id} value={city.city_id}>
                {city.name} ({city.country_iso2})
              </option>
            ))}
            {!cities.some((c) => c.city_id === selected1) && (
              <option value={selected1}>{selected1}</option>
            )}
          </select>
        </div>

        {/* Swap Button */}
        <button
          type="button"
          onClick={handleSwapCities}
          className="p-3 rounded-2xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white transition-all shadow-md shrink-0 mt-4 md:mt-6"
          title="Swap City A and City B"
          aria-label="Swap Cities"
        >
          <ArrowLeftRight className="w-5 h-5 text-indigo-400" />
        </button>

        {/* City 2 Selector */}
        <div className="flex-1 w-full">
          <label htmlFor="city2-select" className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
            City Benchmark B
          </label>
          <select
            id="city2-select"
            value={selected2}
            onChange={(e) => handleCity2Change(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm font-semibold text-white focus:outline-none focus:border-indigo-500 focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            {cities.map((city) => (
              <option key={city.city_id} value={city.city_id}>
                {city.name} ({city.country_iso2})
              </option>
            ))}
            {!cities.some((c) => c.city_id === selected2) && (
              <option value={selected2}>{selected2}</option>
            )}
          </select>
        </div>
      </div>

      {/* Ask AI to Compare Callout */}
      <div className="p-5 rounded-2xl glass-panel border border-indigo-500/30 flex flex-col sm:flex-row items-center justify-between gap-4 bg-indigo-950/20">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-600/20 text-indigo-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Synthesize In-Depth Comparison with Groq AI</h4>
            <p className="text-xs text-slate-400">
              Run multi-agent synthesis comparing {c1?.name || selected1} vs {c2?.name || selected2}.
            </p>
          </div>
        </div>
        <button
          onClick={handleAskAiToCompare}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-1.5 shrink-0"
        >
          <span>Ask AI to Compare</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* City 1 Column */}
        <section aria-label="City Benchmark A" className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                City Benchmark A
              </span>
              <StatusBadge status="database" />
            </div>

            {c1Loading ? (
              <LoadingSkeleton count={3} height="h-20" />
            ) : c1 ? (
              <>
                <div>
                  <h2 className="text-2xl font-bold text-white">{c1.name}</h2>
                  <p className="text-xs text-slate-400">{c1.country_id} ({c1.country_iso2})</p>
                </div>

                <div className="space-y-3 text-xs divide-y divide-slate-800/80">
                  {/* Demographics */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-slate-500" />
                      <span>Population</span>
                    </span>
                    <span className="font-semibold text-white font-mono">
                      {c1.population ? c1.population.toLocaleString() : 'Not documented'}
                    </span>
                  </div>

                  {/* Coordinates */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>Coordinates</span>
                    </span>
                    <span className="font-mono text-slate-300">
                      {c1.latitude.toFixed(2)}°, {c1.longitude.toFixed(2)}°
                    </span>
                  </div>

                  {/* Weather */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Thermometer className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Live Temperature</span>
                    </span>
                    <span className="font-semibold text-white">
                      {c1Weather?.data?.weather?.current?.temperature_c !== undefined
                        ? `${c1Weather.data.weather.current.temperature_c}°C`
                        : <span className="text-slate-500 italic">Unavailable</span>}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400">Condition & Humidity</span>
                    <span className="text-slate-300">
                      {c1Weather?.data?.weather?.current?.condition || '—'}
                      {c1Weather?.data?.weather?.current?.relative_humidity_pct !== undefined &&
                        ` (${c1Weather.data.weather.current.relative_humidity_pct}%)`}
                    </span>
                  </div>

                  {/* Air Quality */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Wind className="w-3.5 h-3.5 text-teal-400" />
                      <span>PM2.5 Air Quality</span>
                    </span>
                    <span className="text-teal-400 font-semibold font-mono">
                      {c1Aqi?.data?.global_weather?.[0]?.pm25 !== undefined
                        ? `${c1Aqi.data.global_weather[0].pm25} µg/m³ (Live)`
                        : (c1Aqi?.data?.who_annual?.[0]?.pm25_annual_mean_ug_m3 ?? c1Aqi?.data?.who_annual?.[0]?.pm25_annual_mean) !== undefined
                        ? `${c1Aqi?.data?.who_annual?.[0]?.pm25_annual_mean_ug_m3 ?? c1Aqi?.data?.who_annual?.[0]?.pm25_annual_mean} µg/m³ (WHO)`
                        : <span className="text-slate-500 italic">Not Available</span>}
                    </span>
                  </div>

                  {/* Cost of Living */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Coins className="w-3.5 h-3.5 text-amber-400" />
                      <span>Consumer Price Index (CPI)</span>
                    </span>
                    <span className="text-amber-400 font-semibold font-mono">
                      {c1Cost?.data?.summary?.consumer_price_index ?? 'Not Indexed'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400">Rent Index</span>
                    <span className="text-amber-300 font-mono">
                      {c1Cost?.data?.summary?.rent_index ?? 'Not Indexed'}
                    </span>
                  </div>

                  {/* Education */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <GraduationCap className="w-3.5 h-3.5 text-purple-400" />
                      <span>Accredited Universities</span>
                    </span>
                    <span className="text-purple-400 font-semibold font-mono">
                      {c1Unis?.data?.length || 0} Institutions
                    </span>
                  </div>

                  {/* Transit */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Bus className="w-3.5 h-3.5 text-blue-400" />
                      <span>Public Transit Registry</span>
                    </span>
                    <span className="text-blue-300">
                      {c1Transit?.data?.transit ? 'Active GTFS Agency' : <span className="text-slate-500 italic">No Feed Registered</span>}
                    </span>
                  </div>

                  {/* Healthcare */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Nearby Healthcare Facilities</span>
                    </span>
                    <span className="text-emerald-400 font-semibold font-mono">
                      {c1Places?.data?.places?.length ?? 0} Facilities (4km)
                    </span>
                  </div>

                  {/* Orchestrator */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Orchestrator Signals</span>
                    </span>
                    <span className="text-indigo-300 font-semibold font-mono">
                      {c1Intel?.data?.signals?.length ?? 0} Signals Mapped
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-4 text-center text-xs text-rose-400">Failed to load City A</div>
            )}
          </div>
        </section>

        {/* City 2 Column */}
        <section aria-label="City Benchmark B" className="space-y-6">
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                City Benchmark B
              </span>
              <StatusBadge status="database" />
            </div>

            {c2Loading ? (
              <LoadingSkeleton count={3} height="h-20" />
            ) : c2 ? (
              <>
                <div>
                  <h2 className="text-2xl font-bold text-white">{c2.name}</h2>
                  <p className="text-xs text-slate-400">{c2.country_id} ({c2.country_iso2})</p>
                </div>

                <div className="space-y-3 text-xs divide-y divide-slate-800/80">
                  {/* Demographics */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-slate-500" />
                      <span>Population</span>
                    </span>
                    <span className="font-semibold text-white font-mono">
                      {c2.population ? c2.population.toLocaleString() : 'Not documented'}
                    </span>
                  </div>

                  {/* Coordinates */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>Coordinates</span>
                    </span>
                    <span className="font-mono text-slate-300">
                      {c2.latitude.toFixed(2)}°, {c2.longitude.toFixed(2)}°
                    </span>
                  </div>

                  {/* Weather */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Thermometer className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Live Temperature</span>
                    </span>
                    <span className="font-semibold text-white">
                      {c2Weather?.data?.weather?.current?.temperature_c !== undefined
                        ? `${c2Weather.data.weather.current.temperature_c}°C`
                        : <span className="text-slate-500 italic">Unavailable</span>}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400">Condition & Humidity</span>
                    <span className="text-slate-300">
                      {c2Weather?.data?.weather?.current?.condition || '—'}
                      {c2Weather?.data?.weather?.current?.relative_humidity_pct !== undefined &&
                        ` (${c2Weather.data.weather.current.relative_humidity_pct}%)`}
                    </span>
                  </div>

                  {/* Air Quality */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Wind className="w-3.5 h-3.5 text-teal-400" />
                      <span>PM2.5 Air Quality</span>
                    </span>
                    <span className="text-teal-400 font-semibold font-mono">
                      {c2Aqi?.data?.global_weather?.[0]?.pm25 !== undefined
                        ? `${c2Aqi.data.global_weather[0].pm25} µg/m³ (Live)`
                        : (c2Aqi?.data?.who_annual?.[0]?.pm25_annual_mean_ug_m3 ?? c2Aqi?.data?.who_annual?.[0]?.pm25_annual_mean) !== undefined
                        ? `${c2Aqi?.data?.who_annual?.[0]?.pm25_annual_mean_ug_m3 ?? c2Aqi?.data?.who_annual?.[0]?.pm25_annual_mean} µg/m³ (WHO)`
                        : <span className="text-slate-500 italic">Not Available</span>}
                    </span>
                  </div>

                  {/* Cost of Living */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Coins className="w-3.5 h-3.5 text-amber-400" />
                      <span>Consumer Price Index (CPI)</span>
                    </span>
                    <span className="text-amber-400 font-semibold font-mono">
                      {c2Cost?.data?.summary?.consumer_price_index ?? 'Not Indexed'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400">Rent Index</span>
                    <span className="text-amber-300 font-mono">
                      {c2Cost?.data?.summary?.rent_index ?? 'Not Indexed'}
                    </span>
                  </div>

                  {/* Education */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <GraduationCap className="w-3.5 h-3.5 text-purple-400" />
                      <span>Accredited Universities</span>
                    </span>
                    <span className="text-purple-400 font-semibold font-mono">
                      {c2Unis?.data?.length || 0} Institutions
                    </span>
                  </div>

                  {/* Transit */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Bus className="w-3.5 h-3.5 text-blue-400" />
                      <span>Public Transit Registry</span>
                    </span>
                    <span className="text-blue-300">
                      {c2Transit?.data?.transit ? 'Active GTFS Agency' : <span className="text-slate-500 italic">No Feed Registered</span>}
                    </span>
                  </div>

                  {/* Healthcare */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Nearby Healthcare Facilities</span>
                    </span>
                    <span className="text-emerald-400 font-semibold font-mono">
                      {c2Places?.data?.places?.length ?? 0} Facilities (4km)
                    </span>
                  </div>

                  {/* Orchestrator */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Orchestrator Signals</span>
                    </span>
                    <span className="text-indigo-300 font-semibold font-mono">
                      {c2Intel?.data?.signals?.length ?? 0} Signals Mapped
                    </span>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-4 text-center text-xs text-rose-400">Failed to load City B</div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};
