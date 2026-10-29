import React, { useState } from 'react';
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
  useCityAirQualityLive,
  useCityCost,
  useCityUniversities,
  useCityTransit,
  useCityPlaces,
  useCityIntelligence,
  useCurrencyConversion,
} from '../hooks/useUrbanLens';
import { StatusBadge } from '../components/StatusBadge';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

const COMPARISON_PRESETS = [
  { c1: 'city_1356226629', c2: 'city_1392685764', label: 'Mumbai vs Tokyo' },
  { c1: 'city_1356226629', c2: 'city_1826645935', label: 'Mumbai vs London' },
  { c1: 'city_1356226629', c2: 'city_1702341000', label: 'Mumbai vs Singapore' },
  { c1: 'city_1356060597', c2: 'city_1392685764', label: 'Kolkata vs Tokyo' },
  { c1: 'city_1356872604', c2: 'city_1784521698', label: 'Delhi vs Dubai' },
];

export const ComparePage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const city1Id = searchParams.get('city1') || 'city_1356226629'; // Default Mumbai
  const city2Id = searchParams.get('city2') || 'city_1392685764'; // Default Tokyo

  const [selected1, setSelected1] = useState(city1Id);
  const [selected2, setSelected2] = useState(city2Id);

  const { data: citiesData } = useCities({ page_size: 50 });
  const cities = citiesData?.data || [];

  // City 1 data queries
  const { data: c1Detail, isLoading: c1Loading } = useCity(selected1);
  const { data: c1Weather } = useCityWeather(selected1);
  const { data: c1AqiLive } = useCityAirQualityLive(selected1);
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
  const { data: c2AqiLive } = useCityAirQualityLive(selected2);
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

  const c1 = c1Detail?.data;
  const c2 = c2Detail?.data;

  const c1Aqi = c1AqiLive?.data?.air_quality;
  const c2Aqi = c2AqiLive?.data?.air_quality;

  // Currencies
  const c1Curr = c1?.currency?.code || 'INR';
  const c2Curr = c2?.currency?.code || 'JPY';

  // Live Currency Conversion between City 1 and City 2
  const { data: fxData } = useCurrencyConversion(c1Curr, c2Curr, 1.0);
  const fx = fxData?.data;

  // 100,000 budget translations
  const { data: budgetData } = useCurrencyConversion(c1Curr, c2Curr, 100000.0);
  const budgetFx = budgetData?.data;

  const { data: inverseBudgetData } = useCurrencyConversion(c2Curr, c1Curr, 100000.0);
  const inverseBudgetFx = inverseBudgetData?.data;

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
    const prompt = `Compare ${c1Name} (${c1Curr}) and ${c2Name} (${c2Curr}) in terms of currency rates, cost of living difference, live air quality, weather, universities, and healthcare. Keep currency rate strictly distinct from cost of living.`;
    navigate(`/ask?q=${encodeURIComponent(prompt)}&cityId=${selected1}`);
  };

  // Cost of Living comparison calculation
  const c1Cpi = c1Cost?.data?.summary?.consumer_price_index;
  const c2Cpi = c2Cost?.data?.summary?.consumer_price_index;
  const bothCostAvailable = c1Cpi != null && c2Cpi != null;
  const oneCostAvailable = (c1Cpi != null && c2Cpi == null) || (c1Cpi == null && c2Cpi != null);

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
          Compare demographics, live weather, real sensor air quality, currency translation, and cost indices head-to-head without fabricated scoring.
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
            Origin City (A)
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
            Destination City (B)
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

      {/* Origin -> Destination Currency & Relocation Translation Section */}
      {c1 && c2 && (
        <div className="glass-panel p-6 rounded-3xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/20 via-slate-900/60 to-slate-900/40 space-y-5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                  Currency & Relocation Translation
                </span>
                {fx && (
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                      fx.status === 'live' || fx.status === 'fresh'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : fx.status === 'cached'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}
                  >
                    {fx.status === 'fresh' ? 'LIVE' : fx.status.toUpperCase()} • {fx.provider}
                  </span>
                )}
              </div>
              <h3 className="text-lg font-black text-white">
                {c1.name} ({c1Curr}) &rarr; {c2.name} ({c2Curr})
              </h3>
            </div>

            <div className="text-right text-xs">
              {fx?.rate ? (
                <>
                  <div className="font-mono font-bold text-base text-white">
                    1 {c1Curr} = <span className="text-emerald-400">{fx.rate.toFixed(4)}</span> {c2Curr}
                  </div>
                  <div className="text-slate-400 text-[11px] mt-0.5">
                    1 {c2Curr} = <span className="font-mono">{fx.inverse_rate != null ? fx.inverse_rate.toFixed(4) : '—'}</span> {c1Curr}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    Updated: {fx.observed_at || (fx.fetched_at ? new Date(fx.fetched_at).toLocaleTimeString() : 'Recent')}
                  </div>
                </>
              ) : (
                <span className="text-slate-500">Live FX Unavailable</span>
              )}
            </div>
          </div>

          {/* Budget Translation & USD Benchmarks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Budget Translation */}
            <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Example Budget Translation
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                  <span className="text-slate-400">
                    {c1.currency?.symbol || ''}100,000 {c1Curr}
                  </span>
                  <span className="font-mono font-bold text-emerald-400">
                    ≈ {c2.currency?.symbol || ''}
                    {budgetFx?.converted_amount
                      ? Math.round(budgetFx.converted_amount).toLocaleString()
                      : '—'}{' '}
                    {c2Curr}
                  </span>
                </div>
                <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                  <span className="text-slate-400">
                    {c2.currency?.symbol || ''}100,000 {c2Curr}
                  </span>
                  <span className="font-mono font-bold text-emerald-400">
                    ≈ {c1.currency?.symbol || ''}
                    {inverseBudgetFx?.converted_amount
                      ? Math.round(inverseBudgetFx.converted_amount).toLocaleString()
                      : '—'}{' '}
                    {c1Curr}
                  </span>
                </div>
              </div>
            </div>

            {/* USD Benchmark */}
            <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                USD Benchmark (Relative Currency Strength)
              </h4>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                  <span className="text-slate-400">{c1.name} ({c1Curr})</span>
                  <span className="font-mono font-bold text-cyan-400">
                    {fx?.usd_benchmark_base?.rate_to_usd != null ? `1 ${c1Curr} = $${fx.usd_benchmark_base.rate_to_usd.toFixed(4)} USD` : 'Unavailable'}
                  </span>
                </div>
                <div className="flex justify-between items-center p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                  <span className="text-slate-400">{c2.name} ({c2Curr})</span>
                  <span className="font-mono font-bold text-cyan-400">
                    {fx?.usd_benchmark_quote?.rate_to_usd != null ? `1 ${c2Curr} = $${fx.usd_benchmark_quote.rate_to_usd.toFixed(4)} USD` : 'Unavailable'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Cost of Living Distinction */}
          <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-300">Cost-of-Living Baseline Comparison</span>
              <span className="text-[11px] text-slate-500">Distinct from currency FX</span>
            </div>

            {bothCostAvailable && c1Cpi != null && c2Cpi != null ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex justify-between">
                  <span className="text-slate-400">CPI Difference ({c1.name} vs {c2.name}):</span>
                  <span className="font-mono font-bold text-amber-400">
                    {c1Cpi} vs {c2Cpi} ({Number(c2Cpi) > Number(c1Cpi) ? `+${((Number(c2Cpi) - Number(c1Cpi)) / Number(c1Cpi) * 100).toFixed(1)}%` : `${((Number(c2Cpi) - Number(c1Cpi)) / Number(c1Cpi) * 100).toFixed(1)}%`})
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 flex justify-between">
                  <span className="text-slate-400">Rent Index:</span>
                  <span className="font-mono font-bold text-amber-400">
                    {c1Cost?.data?.summary?.rent_index ?? '—'} vs {c2Cost?.data?.summary?.rent_index ?? '—'}
                  </span>
                </div>
              </div>
            ) : oneCostAvailable ? (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
                Cost comparison unavailable — verified data exists for only one city.
              </div>
            ) : (
              <div className="text-slate-500 italic">
                Cost comparison unavailable — neither city has recorded Numbeo consumer basket baselines.
              </div>
            )}
          </div>
        </div>
      )}

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
                  <p className="text-xs text-slate-400">
                    {c1.country_id} ({c1.country_iso2}) • Currency: {c1Curr} ({c1.currency?.symbol || ''})
                  </p>
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

                  {/* Air Quality */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Wind className="w-3.5 h-3.5 text-teal-400" />
                      <span>Air Quality (PM2.5)</span>
                    </span>
                    <span className="text-teal-400 font-semibold font-mono">
                      {c1Aqi?.pollutants?.pm25 !== undefined && c1Aqi.pollutants.pm25 !== null ? (
                        <>
                          {c1Aqi.pollutants.pm25} µg/m³{' '}
                          <span className="text-[10px] text-slate-400">
                            ({(c1Aqi.status || 'data').toUpperCase()})
                          </span>
                        </>
                      ) : (
                        <span className="text-slate-500 italic">Not Available</span>
                      )}
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
                  <p className="text-xs text-slate-400">
                    {c2.country_id} ({c2.country_iso2}) • Currency: {c2Curr} ({c2.currency?.symbol || ''})
                  </p>
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

                  {/* Air Quality */}
                  <div className="flex items-center justify-between py-2.5">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Wind className="w-3.5 h-3.5 text-teal-400" />
                      <span>Air Quality (PM2.5)</span>
                    </span>
                    <span className="text-teal-400 font-semibold font-mono">
                      {c2Aqi?.pollutants?.pm25 !== undefined && c2Aqi.pollutants.pm25 !== null ? (
                        <>
                          {c2Aqi.pollutants.pm25} µg/m³{' '}
                          <span className="text-[10px] text-slate-400">
                            ({(c2Aqi.status || 'data').toUpperCase()})
                          </span>
                        </>
                      ) : (
                        <span className="text-slate-500 italic">Not Available</span>
                      )}
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
