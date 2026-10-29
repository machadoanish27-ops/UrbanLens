import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Compass,
  Thermometer,
  Wind,
  Coins,
  GraduationCap,
  Bus,
  Sparkles,
  MapPin,
  Users,
  AlertTriangle,
  ExternalLink,
  Layers,
  Calendar,
  Eye,
  RefreshCw,
  Building2,
  Navigation,
  ArrowRight,
  ArrowLeftRight,
  Phone,
  Clock,
  HeartPulse,
} from 'lucide-react';
import {
  useCity,
  useCityWeather,
  useCityAirQualityLive,
  useCityCost,
  useCityTransit,
  useCityIntelligence,
  useCityEducation,
  useCityHealthcare,
  useCurrencyConversion,
} from '../hooks/useUrbanLens';
import { useOriginDestination } from '../context/OriginDestinationContext';
import { StatusBadge } from '../components/StatusBadge';
import { ProvenanceTag } from '../components/ProvenanceTag';
import { MetricCard } from '../components/MetricCard';
import { EvidenceCard } from '../components/EvidenceCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { InteractiveMap, type MapMarkerItem } from '../components/InteractiveMap';

type TabKey =
  | 'overview'
  | 'relocation'
  | 'map'
  | 'weather'
  | 'airQuality'
  | 'cost'
  | 'education'
  | 'healthcare'
  | 'transit'
  | 'agents';

const EDU_FILTER_TYPES = [
  { key: 'all', label: 'All Institutions' },
  { key: 'University', label: 'Universities' },
  { key: 'College', label: 'Colleges' },
  { key: 'Engineering College', label: 'Engineering' },
  { key: 'Medical College', label: 'Medical' },
  { key: 'Business School', label: 'Business' },
  { key: 'School', label: 'Schools' },
  { key: 'Technical Institute', label: 'Technical' },
];

const HEALTH_FILTER_CATEGORIES = [
  { key: 'all', label: 'All Facilities', emoji: '🌐' },
  { key: 'hospital', label: 'Hospitals', emoji: '🏨' },
  { key: 'clinic', label: 'Clinics', emoji: '🩺' },
  { key: 'dental', label: 'Dental Clinics', emoji: '🦷' },
  { key: 'pharmacy', label: 'Pharmacies', emoji: '💊' },
  { key: 'urgent_care', label: 'Urgent Care', emoji: '🚨' },
];

export const CityPage: React.FC = () => {
  const { cityId } = useParams<{ cityId: string }>();
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [selectedEduType, setSelectedEduType] = useState<string>('all');
  const [selectedHealthCategory, setSelectedHealthCategory] = useState<string>('all');

  // Origin & Destination Context
  const { origin, setDestination, openOriginModal } = useOriginDestination();

  // Primary Canonical City Query
  const {
    data: cityData,
    isLoading: cityLoading,
    error: cityError,
    refetch: refetchCity,
    isRefetching: isRefetchingCity,
  } = useCity(cityId || '');

  const city = cityData?.data;

  // Sync Destination when City loads
  useEffect(() => {
    if (city) {
      setDestination({
        city_id: city.city_id,
        city_name: city.name,
        country_name: city.country_id,
        country_iso2: city.country_iso2,
        currency_code: city.currency?.code || 'USD',
        currency_symbol: city.currency?.symbol || '$',
        currency_name: city.currency?.name || 'US Dollar',
      });
    }
  }, [city, setDestination]);

  // Live Currency Conversion: Origin -> Destination
  const baseCurrency = origin.currency_code || 'INR';
  const destCurrency = city?.currency?.code || 'USD';

  const {
    data: fxData,
    isLoading: fxLoading,
    refetch: refetchFx,
    isRefetching: isRefetchingFx,
  } = useCurrencyConversion(baseCurrency, destCurrency, 1.0);
  const fx = fxData?.data;

  // Budget conversions
  const { data: budgetData } = useCurrencyConversion(baseCurrency, destCurrency, 100000.0);
  const budgetFx = budgetData?.data;

  const { data: inverseBudgetData } = useCurrencyConversion(destCurrency, baseCurrency, 100000.0);
  const inverseBudgetFx = inverseBudgetData?.data;

  // Live Weather Query
  const {
    data: weatherData,
    isLoading: weatherLoading,
    refetch: refetchWeather,
    isRefetching: isRefetchingWeather,
  } = useCityWeather(cityId || '');

  // Live Air Quality Query (OpenAQ with WHO fallback)
  const {
    data: aqiLiveData,
    isLoading: aqiLiveLoading,
    refetch: refetchAqiLive,
    isRefetching: isRefetchingAqiLive,
  } = useCityAirQualityLive(cityId || '');
  const aqiData = aqiLiveData?.data?.air_quality;

  // Cost of Living Query
  const {
    data: costData,
    isLoading: costLoading,
    refetch: refetchCost,
    isRefetching: isRefetchingCost,
  } = useCityCost(cityId || '');

  // Education Discovery Query (Canonical DB + OSM)
  const {
    data: eduData,
    isLoading: eduLoading,
    refetch: refetchEdu,
    isRefetching: isRefetchingEdu,
  } = useCityEducation(
    cityId || '',
    selectedEduType === 'all' ? undefined : selectedEduType,
    1,
    40
  );
  const education = eduData?.data;

  // Healthcare Discovery Query (OSM Overpass with contact details)
  const {
    data: healthData,
    isLoading: healthLoading,
    refetch: refetchHealth,
    isRefetching: isRefetchingHealth,
  } = useCityHealthcare(
    cityId || '',
    selectedHealthCategory === 'all' ? undefined : selectedHealthCategory,
    5000,
    35
  );
  const healthcare = healthData?.data;

  // Transit Query
  const {
    data: transitData,
    isLoading: transitLoading,
    refetch: refetchTransit,
    isRefetching: isRefetchingTransit,
  } = useCityTransit(cityId || '');

  // Multi-Agent Intelligence Query
  const {
    data: intelData,
    isLoading: intelLoading,
    refetch: refetchIntel,
    isRefetching: isRefetchingIntel,
  } = useCityIntelligence(cityId || '');

  const weather = weatherData?.data?.weather;
  const weatherMeta = weatherData?.data?.meta;
  const cost = costData?.data;
  const transit = transitData?.data;
  const intelligence = intelData?.data;

  // Build combined map markers from Education institutions & Healthcare facilities
  const mapMarkers: MapMarkerItem[] = useMemo(() => {
    const list: MapMarkerItem[] = [];

    // Education markers
    (education?.institutions || []).forEach((inst) => {
      if (inst.latitude && inst.longitude) {
        list.push({
          lat: inst.latitude,
          lon: inst.longitude,
          title: inst.name,
          category: inst.type,
          address: inst.address || `${inst.city}, ${inst.country}`,
          provider: inst.provider,
          website: inst.website || undefined,
        });
      }
    });

    // Healthcare markers
    (healthcare?.facilities || []).forEach((fac) => {
      if (fac.latitude && fac.longitude) {
        list.push({
          lat: fac.latitude,
          lon: fac.longitude,
          title: fac.name,
          category: fac.type,
          address: fac.address || undefined,
          distance_meters: fac.distance_meters || undefined,
          provider: fac.provider,
          website: fac.website || undefined,
          phone: fac.phone || undefined,
        });
      }
    });

    return list;
  }, [education, healthcare]);

  if (cityLoading) {
    return (
      <div className="space-y-6 max-w-6xl mx-auto py-8">
        <LoadingSkeleton count={1} height="h-32" />
        <LoadingSkeleton count={3} height="h-48" />
      </div>
    );
  }

  if (cityError || !city) {
    return (
      <div className="glass-panel p-8 rounded-2xl border border-rose-500/30 text-center max-w-2xl mx-auto my-12">
        <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">City Not Found or Server Unreachable</h2>
        <p className="text-sm text-slate-400 mb-6">
          We could not locate data for city ID <code className="text-rose-300">{cityId}</code> in the canonical store.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors"
        >
          <Compass className="w-4 h-4" />
          <span>Back to City Explorer</span>
        </Link>
      </div>
    );
  }

  const tabs: { key: TabKey; label: string; icon: React.ReactNode }[] = [
    { key: 'overview', label: 'Overview', icon: <Eye className="w-4 h-4" /> },
    { key: 'relocation', label: 'Relocation & Currency', icon: <ArrowLeftRight className="w-4 h-4" /> },
    { key: 'map', label: 'Interactive Map', icon: <MapPin className="w-4 h-4" /> },
    { key: 'weather', label: 'Live Weather', icon: <Thermometer className="w-4 h-4" /> },
    { key: 'airQuality', label: 'Air Quality', icon: <Wind className="w-4 h-4" /> },
    { key: 'cost', label: 'Cost of Living', icon: <Coins className="w-4 h-4" /> },
    { key: 'education', label: 'Education Discovery', icon: <GraduationCap className="w-4 h-4" /> },
    { key: 'healthcare', label: 'Healthcare Discovery', icon: <HeartPulse className="w-4 h-4" /> },
    { key: 'transit', label: 'Mobility & Transit', icon: <Bus className="w-4 h-4" /> },
    { key: 'agents', label: 'AI Intelligence', icon: <Layers className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* City Header Banner */}
      <section className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 relative overflow-hidden shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {city.country_iso2} • {city.country_id}
              </span>
              <StatusBadge status="database" label="Atlas Canonical Record" />
              {city.currency && (
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {city.currency.code} ({city.currency.symbol})
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-white tracking-tight">
              {city.name}
            </h1>

            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mt-2">
              {city.admin_name && <span>Region: {city.admin_name}</span>}
              <span>•</span>
              <span className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5 text-slate-500" />
                Pop: {city.population ? city.population.toLocaleString() : 'Not documented'}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1 font-mono text-[11px]">
                <Navigation className="w-3.5 h-3.5 text-slate-500" />
                {city.latitude.toFixed(4)}°N, {city.longitude.toFixed(4)}°E
              </span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => refetchCity()}
              disabled={isRefetchingCity}
              className="px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium transition-all flex items-center gap-1.5"
              title="Refresh canonical profile"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefetchingCity ? 'animate-spin text-indigo-400' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
            <Link
              to={`/compare?city1=${encodeURIComponent(city.city_id)}`}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all flex items-center gap-2"
            >
              <span>Compare</span>
            </Link>
            <Link
              to={`/ask?cityId=${encodeURIComponent(city.city_id)}`}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-white" />
              <span>Ask AI Intelligence</span>
            </Link>
          </div>
        </div>

        {/* Tab Navigation */}
        <div
          role="tablist"
          aria-label="City Data Tabs"
          className="mt-8 pt-4 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none"
        >
          {tabs.map((tab) => (
            <button
              key={tab.key}
              role="tab"
              aria-selected={activeTab === tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                activeTab === tab.key
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-slate-800/80'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Relocation Snapshot Card */}
          <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 bg-gradient-to-r from-indigo-950/20 via-slate-900/60 to-slate-900/40">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                  <ArrowLeftRight className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                      Relocation Snapshot
                    </span>
                    <button
                      onClick={openOriginModal}
                      className="text-[11px] text-indigo-300 hover:text-white underline decoration-indigo-500/50"
                    >
                      (Change Origin)
                    </button>
                  </div>
                  <h3 className="text-base font-bold text-white mt-0.5">
                    {origin.city_name}, {origin.country_name} ({origin.currency_code} {origin.currency_symbol}) &rarr; {city.name}, {city.country_id} ({destCurrency} {city.currency?.symbol || ''})
                  </h3>
                </div>
              </div>

              {/* Quick FX pill */}
              <div className="flex items-center gap-3">
                {fx ? (
                  <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-right">
                    <div className="text-xs font-semibold text-slate-300">
                      1 {origin.currency_code} = <span className="text-emerald-400 font-mono font-bold">{fx.rate?.toFixed(4)}</span> {destCurrency}
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5">
                      1 {destCurrency} = <span className="font-mono">{fx.inverse_rate != null ? fx.inverse_rate.toFixed(4) : '—'}</span> {origin.currency_code} • {fx.provider}
                    </div>
                  </div>
                ) : fxLoading ? (
                  <div className="text-xs text-slate-400 animate-pulse">Loading live FX...</div>
                ) : (
                  <div className="text-xs text-slate-500">Live rate unavailable</div>
                )}
                <button
                  onClick={() => setActiveTab('relocation')}
                  className="px-3.5 py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600 border border-indigo-500/40 text-indigo-200 text-xs font-semibold transition-all whitespace-nowrap"
                >
                  Full Relocation View &rarr;
                </button>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Population"
              value={city.population}
              icon={<Users className="w-4 h-4" />}
              status="database"
              subValue="Canonical WorldCities Record"
            />
            <MetricCard
              label="Live Temperature"
              value={weather?.current?.temperature_c}
              unit="°C"
              icon={<Thermometer className="w-4 h-4" />}
              status={weatherMeta?.status || 'unavailable'}
              subValue={weather?.current?.condition || 'Real-time observation'}
            />
            <MetricCard
              label="Air Quality (PM2.5)"
              value={aqiData?.pollutants?.pm25}
              unit="µg/m³"
              icon={<Wind className="w-4 h-4" />}
              status={aqiData?.status === 'live' ? 'fresh' : aqiData?.status === 'database' ? 'database' : 'unavailable'}
              subValue={
                aqiData
                  ? `${aqiData.provider} (${(aqiData.status || 'data').toUpperCase()})`
                  : 'Sensors Unavailable'
              }
            />
            <MetricCard
              label="Institutions Indexed"
              value={education ? `${education.total.toLocaleString()} Total (${education.displayed_count ?? education.institutions.length} Shown)` : '—'}
              icon={<GraduationCap className="w-4 h-4" />}
              status="database"
              subValue={
                education
                  ? `${education.canonical_count || 0} Universities, ${education.community_mapped_count || 0} Colleges/Schools`
                  : 'Canonical Directory'
              }
            />
          </div>

          {/* Interactive Mini-Map Preview */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                <span>Geographic Anchor & Mapped Institutions / Facilities</span>
              </span>
              <button
                onClick={() => setActiveTab('map')}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
              >
                Expand Full Interactive Map ({mapMarkers.length} POIs) &rarr;
              </button>
            </div>
            <InteractiveMap
              latitude={city.latitude}
              longitude={city.longitude}
              cityName={city.name}
              markers={mapMarkers.slice(0, 15)}
              height="h-64"
            />
          </div>

          {/* Multi-Agent Summary Banner */}
          {intelligence?.summary && (
            <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 bg-indigo-950/20">
              <div className="flex items-center gap-2 mb-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                <span>Multi-Agent Grounded Overview</span>
              </div>
              <p className="text-slate-200 text-sm leading-relaxed">{intelligence.summary}</p>
            </div>
          )}

          {/* Registry Identifiers */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-4">Canonical Registry Identifiers</h3>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block mb-1">City ID (Slug)</span>
                <span className="font-mono text-slate-200 font-semibold">{city.city_id}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block mb-1">Country ISO Alpha-2 / Alpha-3</span>
                <span className="font-mono text-slate-200 font-semibold">
                  {city.country_iso2} / {city.country_iso3 || 'N/A'}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block mb-1">Official Currency</span>
                <span className="font-mono text-emerald-400 font-semibold">
                  {city.currency?.code || 'USD'} ({city.currency?.symbol || '$'}) • {city.currency?.name || ''}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-slate-500 block mb-1">WorldCities ID</span>
                <span className="font-mono text-slate-200 font-semibold">
                  {city.worldcities_id || 'Canonical'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Relocation & Currency */}
      {activeTab === 'relocation' && (
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <ArrowLeftRight className="w-5 h-5 text-indigo-400" />
                <span>Origin &rarr; Destination Relocation Translation</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time exchange conversion between origin currency and destination currency, strictly distinct from cost-of-living purchasing power.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={openOriginModal}
                className="px-3.5 py-1.5 rounded-xl bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 text-xs font-semibold border border-indigo-500/40 transition-colors"
              >
                Change Origin
              </button>
              <button
                onClick={() => refetchFx()}
                disabled={isRefetchingFx}
                className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                title="Refresh rates"
              >
                <RefreshCw className={`w-3 h-3 ${isRefetchingFx ? 'animate-spin text-indigo-400' : ''}`} />
                <span>Refresh FX</span>
              </button>
            </div>
          </div>

          {/* Context Banner */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-2">
              <span className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">
                FROM
              </span>
              <div className="text-xl font-black text-white">
                {origin.city_name}, {origin.country_name}
              </div>
              <div className="text-xs text-slate-300 font-mono font-bold">
                {origin.currency_code} ({origin.currency_symbol})
              </div>
              <div className="text-[11px] text-slate-500">
                Source: {origin.source}
              </div>
            </div>

            <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-2">
              <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">
                TO
              </span>
              <div className="text-xl font-black text-white">
                {city.name}, {city.country_id}
              </div>
              <div className="text-xs text-slate-300 font-mono font-bold">
                {destCurrency} ({city.currency?.symbol || ''})
              </div>
              <div className="text-[11px] text-slate-500">
                Source: Canonical Atlas City Record ({city.country_iso2})
              </div>
            </div>
          </div>

          {/* Live Rates & Budget Translation Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Direct & Inverse Rates */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-bold text-white">Official Exchange Rate Snapshot</h4>
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

              {fxLoading ? (
                <LoadingSkeleton count={2} height="h-16" />
              ) : fx?.rate ? (
                <div className="space-y-3">
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-mono">1 {origin.currency_code} =</span>
                    <span className="text-lg font-mono font-bold text-white">
                      <span className="text-emerald-400">{fx.rate.toFixed(4)}</span> {destCurrency}
                    </span>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-mono">1 {destCurrency} =</span>
                    <span className="text-lg font-mono font-bold text-white">
                      <span className="text-emerald-400">{fx.inverse_rate != null ? fx.inverse_rate.toFixed(4) : '—'}</span> {origin.currency_code}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] text-slate-400">
                    <div>
                      <span className="text-slate-500 block">Provider:</span>
                      <span className="font-semibold text-slate-200">{fx.provider}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Status:</span>
                      <span className={`font-bold ${fx.status === 'live' || fx.status === 'fresh' ? 'text-emerald-400' : fx.status === 'cached' ? 'text-amber-400' : 'text-rose-400'}`}>
                        {(fx.status === 'fresh' ? 'LIVE' : fx.status).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Updated:</span>
                      <span className="font-mono text-slate-200">{fx.observed_at || (fx.fetched_at ? new Date(fx.fetched_at).toLocaleTimeString() : 'Recent')}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-4 text-center rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
                  Live FX rate currently unavailable between {origin.currency_code} and {destCurrency}.
                </div>
              )}
            </div>

            {/* Example Monthly Budget Translation */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <h4 className="text-sm font-bold text-white">Example Budget Translation</h4>
              <p className="text-xs text-slate-400">
                Nominal currency translation for equivalent numerical sums (before local cost-of-living adjustments).
              </p>

              <div className="space-y-3">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                  <span className="text-[11px] text-slate-400">Monthly Budget (Origin)</span>
                  <div className="text-base font-mono font-bold text-slate-200">
                    {origin.currency_symbol}100,000 {origin.currency_code}
                  </div>
                  <div className="text-xs text-emerald-400 font-mono font-semibold flex items-center gap-1">
                    <ArrowRight className="w-3.5 h-3.5" />
                    <span>
                      ≈ {city.currency?.symbol || ''}
                      {budgetFx?.converted_amount
                        ? Math.round(budgetFx.converted_amount).toLocaleString()
                        : '—'}{' '}
                      {destCurrency}
                    </span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                  <span className="text-[11px] text-slate-400">Inverse Monthly Budget (Destination)</span>
                  <div className="text-base font-mono font-bold text-slate-200">
                    {city.currency?.symbol || ''}100,000 {destCurrency}
                  </div>
                  <div className="text-xs text-emerald-400 font-mono font-semibold flex items-center gap-1">
                    <ArrowRight className="w-3.5 h-3.5" />
                    <span>
                      ≈ {origin.currency_symbol}
                      {inverseBudgetFx?.converted_amount
                        ? Math.round(inverseBudgetFx.converted_amount).toLocaleString()
                        : '—'}{' '}
                      {origin.currency_code}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* USD Benchmark Section */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-white">USD Relative Strength Benchmark</h4>
                <p className="text-xs text-slate-400">
                  Relative currency strength anchored against the US Dollar (strictly labelled USD benchmark, not "highest currency").
                </p>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                USD Reference Base
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-500 block mb-1">
                  Origin Currency ({origin.currency_code}) USD Benchmark
                </span>
                <span className="text-base font-mono font-bold text-slate-200">
                  {fx?.usd_benchmark_base?.rate_to_usd != null ? (
                    <>
                      1 {origin.currency_code} = <span className="text-cyan-400">${fx.usd_benchmark_base.rate_to_usd.toFixed(4)} USD</span>
                    </>
                  ) : (
                    'Benchmark Unavailable'
                  )}
                </span>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                <span className="text-xs text-slate-500 block mb-1">
                  Destination Currency ({destCurrency}) USD Benchmark
                </span>
                <span className="text-base font-mono font-bold text-slate-200">
                  {fx?.usd_benchmark_quote?.rate_to_usd != null ? (
                    <>
                      1 {destCurrency} = <span className="text-cyan-400">${fx.usd_benchmark_quote.rate_to_usd.toFixed(4)} USD</span>
                    </>
                  ) : (
                    'Benchmark Unavailable'
                  )}
                </span>
              </div>
            </div>
          </div>

          {/* Critical Distinction Notice */}
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 space-y-1">
            <strong>Critical Analytical Distinction:</strong> Currency conversion measures nominal foreign exchange pricing only. It does not mean purchasing power or local living costs are normalized. To inspect real grocery, rent, and utility baselines, see the separate <em>Cost of Living</em> section below.
          </div>
        </div>
      )}

      {/* Tab 3: Interactive Map */}
      {activeTab === 'map' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-indigo-400" />
                <span>Interactive Geographic Intelligence Map</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Grounded coordinates for {city.name} with category-filtered discovery of universities, colleges, hospitals, clinics, dental facilities, and pharmacies.
              </p>
            </div>
            <ProvenanceTag source="OpenStreetMap (ODbL) & Canonical DB" confidence={1.0} />
          </div>

          <InteractiveMap
            latitude={city.latitude}
            longitude={city.longitude}
            cityName={city.name}
            markers={mapMarkers}
            zoom={13}
            height="h-[560px]"
            showFilters={true}
          />
        </div>
      )}

      {/* Tab 4: Live Weather */}
      {activeTab === 'weather' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Thermometer className="w-5 h-5 text-indigo-400" />
                <span>Real-Time Atmospheric Conditions</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Official WMO station forecasts and ground-truth meteorological observations.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => refetchWeather()}
                disabled={isRefetchingWeather}
                className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                title="Refetch live weather"
              >
                <RefreshCw className={`w-3 h-3 ${isRefetchingWeather ? 'animate-spin text-indigo-400' : ''}`} />
                <span>Refetch Live</span>
              </button>
              {weatherMeta && (
                <ProvenanceTag
                  source={weatherMeta.provider || 'Open-Meteo API'}
                  observedAt={weatherMeta.observed_at}
                  confidence={weatherMeta.confidence}
                />
              )}
            </div>
          </div>

          {weatherLoading ? (
            <LoadingSkeleton count={2} height="h-32" />
          ) : weather ? (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                <MetricCard
                  label="Temperature"
                  value={weather.current.temperature_c}
                  unit="°C"
                  status={weatherMeta?.status}
                  subValue={weather.current.condition || undefined}
                />
                <MetricCard
                  label="Feels Like"
                  value={weather.current.apparent_temperature_c}
                  unit="°C"
                  status={weatherMeta?.status}
                />
                <MetricCard
                  label="Humidity"
                  value={weather.current.relative_humidity_pct}
                  unit="%"
                  status={weatherMeta?.status}
                />
                <MetricCard
                  label="Wind Speed"
                  value={weather.current.wind_speed_kph}
                  unit="km/h"
                  status={weatherMeta?.status}
                />
                <MetricCard
                  label="Precipitation"
                  value={weather.current.precipitation_mm}
                  unit="mm"
                  status={weatherMeta?.status}
                />
                <MetricCard
                  label="Pressure"
                  value={weather.current.surface_pressure_mb}
                  unit="hPa"
                  status={weatherMeta?.status}
                />
              </div>

              {/* 7-Day Forecast */}
              {weather.daily_forecasts && weather.daily_forecasts.length > 0 && (
                <div className="glass-panel p-6 rounded-2xl border border-slate-800">
                  <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-cyan-400" />
                    <span>7-Day Weather Outlook</span>
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                    {weather.daily_forecasts.map((df, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-center flex flex-col justify-between"
                      >
                        <span className="text-[11px] font-medium text-slate-400">
                          {new Date(df.date).toLocaleDateString(undefined, {
                            weekday: 'short',
                            month: 'numeric',
                            day: 'numeric',
                          })}
                        </span>
                        <div className="my-2">
                          <span className="text-base font-bold text-white">{df.temp_max_c}°</span>
                          <span className="text-xs text-slate-500 ml-1">{df.temp_min_c}°</span>
                        </div>
                        <span className="text-[10px] text-slate-400 truncate" title={df.condition || ''}>
                          {df.condition || 'Clear'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">Weather Data Currently Unavailable</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Air Quality */}
      {activeTab === 'airQuality' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Wind className="w-5 h-5 text-teal-400" />
                <span>Live Air Quality & Atmospheric Pollution</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Primary: OpenAQ live sensor API • Fallback: MongoDB / WHO historical annual standards.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => refetchAqiLive()}
                disabled={isRefetchingAqiLive}
                className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                title="Refetch live air quality"
              >
                <RefreshCw className={`w-3 h-3 ${isRefetchingAqiLive ? 'animate-spin text-indigo-400' : ''}`} />
                <span>Refetch AQI</span>
              </button>
              {aqiData && (
                <span
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${
                    aqiData.status === 'live'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : aqiData.status === 'database'
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}
                >
                  Status: {aqiData.status} ({aqiData.provider})
                </span>
              )}
            </div>
          </div>

          {/* Warning banner when fallback database observation is used */}
          {aqiData?.warning && (
            <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-xs text-amber-300">
                <strong>Data Provenance Notice:</strong> {aqiData.warning}
              </div>
            </div>
          )}

          {aqiLiveLoading ? (
            <LoadingSkeleton count={2} height="h-32" />
          ) : aqiData ? (
            <div className="space-y-6">
              {/* Pollutants Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                  label="PM2.5 (Fine Particulates)"
                  value={aqiData.pollutants?.pm25}
                  unit="µg/m³"
                  status={aqiData.status === 'live' ? 'fresh' : 'database'}
                  subValue={
                    aqiData.pollutants?.pm25 !== undefined && aqiData.pollutants?.pm25 !== null
                      ? aqiData.pollutants.pm25 > 15
                        ? 'Exceeds WHO 24h Guide'
                        : 'Within WHO 24h Guide'
                      : undefined
                  }
                />
                <MetricCard
                  label="PM10 (Respirable)"
                  value={aqiData.pollutants?.pm10}
                  unit="µg/m³"
                  status={aqiData.status === 'live' ? 'fresh' : 'database'}
                  subValue="Coarse particulate matter"
                />
                <MetricCard
                  label="NO₂ (Nitrogen Dioxide)"
                  value={aqiData.pollutants?.no2}
                  unit="µg/m³"
                  status={aqiData.status === 'live' ? 'fresh' : 'database'}
                  subValue="Traffic & combustion emissions"
                />
                <MetricCard
                  label="O₃ (Ozone)"
                  value={aqiData.pollutants?.o3}
                  unit="µg/m³"
                  status={aqiData.status === 'live' ? 'fresh' : 'database'}
                  subValue="Photochemical oxidant"
                />
              </div>

              {/* Provenance Box */}
              <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-2 text-xs">
                <h4 className="text-sm font-bold text-white">Air Quality Provenance Audit</h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Provider Source</span>
                    <span className="font-semibold text-slate-200">{aqiData.provider}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Observed At</span>
                    <span className="font-mono text-slate-200">{aqiData.observed_at || 'Annual / Historical'}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Live Status Flag</span>
                    <span className="font-semibold text-slate-200">{aqiData.is_live ? 'Yes (Live)' : 'No (Database/Historical)'}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">No Air Quality Records Registered</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 6: Cost of Living */}
      {activeTab === 'cost' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Coins className="w-5 h-5 text-amber-400" />
                <span>Cost of Living Indices & Consumer Pricing</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Standardized consumer price baskets and residential rent comparisons.
              </p>
            </div>

            <button
              onClick={() => refetchCost()}
              disabled={isRefetchingCost}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
              title="Refetch cost data"
            >
              <RefreshCw className={`w-3 h-3 ${isRefetchingCost ? 'animate-spin text-indigo-400' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>

          {costLoading ? (
            <LoadingSkeleton count={2} height="h-32" />
          ) : cost && (cost.metrics?.length > 0 || cost.summary) ? (
            <div className="space-y-6">
              {cost.summary && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <MetricCard
                    label="Consumer Price Index (CPI)"
                    value={cost.summary.consumer_price_index}
                    status="database"
                    subValue="Base 100 benchmark"
                  />
                  <MetricCard
                    label="Rent Index"
                    value={cost.summary.rent_index}
                    status="database"
                    subValue="Relative to reference baseline"
                  />
                  <MetricCard
                    label="Purchasing Power"
                    value={cost.summary.purchasing_power_index}
                    status="database"
                    subValue="Domestic purchasing capability"
                  />
                </div>
              )}

              {cost.metrics && cost.metrics.length > 0 && (
                <div className="glass-panel p-6 rounded-2xl border border-slate-800">
                  <h4 className="text-sm font-bold text-white mb-4">Detailed Expense Breakdown</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {cost.metrics.map((m, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center text-xs"
                      >
                        <span className="text-slate-300 font-medium">{m.metric}</span>
                        <span className="text-amber-400 font-bold font-mono">
                          {m.value} {m.currency || ''}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">Cost of Living Records Not Available</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 7: Education Discovery */}
      {activeTab === 'education' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <GraduationCap className="w-5 h-5 text-purple-400" />
                <span>Education Discovery & Institutional Ecosystem</span>
              </h3>
              <div className="flex flex-wrap items-center gap-2 mt-1.5">
                <span className="px-2.5 py-0.5 rounded-lg bg-purple-600/20 text-purple-300 border border-purple-500/30 text-xs font-bold tracking-wide">
                  {education ? `${education.total.toLocaleString()} INDEXED INSTITUTIONS` : '—'}
                </span>
                <span className="px-2.5 py-0.5 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold">
                  Showing {education ? (education.displayed_count ?? education.institutions.length) : 0}
                </span>
                <span className="text-xs text-slate-400">
                  • {education?.canonical_count || 0} canonical universities, {education?.community_mapped_count || 0} mapped colleges/schools
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => refetchEdu()}
                disabled={isRefetchingEdu}
                className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                title="Refetch education"
              >
                <RefreshCw className={`w-3 h-3 ${isRefetchingEdu ? 'animate-spin text-indigo-400' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {/* Type Filter Chips */}
          <div className="flex flex-wrap gap-2">
            {EDU_FILTER_TYPES.map((f) => (
              <button
                key={f.key}
                type="button"
                onClick={() => setSelectedEduType(f.key)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  selectedEduType === f.key
                    ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Honest Disclaimer */}
          {education?.disclaimer && (
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 text-xs">
              <strong>Coverage Scope:</strong> {education.disclaimer}
            </div>
          )}

          {/* Institutions Grid */}
          {eduLoading ? (
            <LoadingSkeleton count={4} height="h-28" />
          ) : education?.institutions && education.institutions.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {education.institutions.map((inst) => (
                <div
                  key={inst.institution_id}
                  className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h4 className="text-base font-bold text-white">{inst.name}</h4>
                        <span className="text-[11px] font-semibold text-purple-300 uppercase tracking-wide">
                          {inst.type}
                        </span>
                      </div>

                      {/* Official Website or Unavailable */}
                      {inst.website ? (
                        <a
                          href={inst.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 rounded-lg bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600 hover:text-white text-xs font-semibold inline-flex items-center gap-1 transition-all shrink-0"
                        >
                          <span>Official Website</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-[11px] text-slate-500 italic shrink-0">Website unavailable</span>
                      )}
                    </div>

                    {inst.address && (
                      <p className="text-xs text-slate-400 mt-1 line-clamp-1">{inst.address}</p>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="font-mono">
                      {inst.city}, {inst.country}
                    </span>
                    <span className="font-semibold text-slate-400">
                      Source: {inst.provider}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <GraduationCap className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">No Institutions Matching "{selectedEduType}"</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 8: Healthcare Discovery */}
      {activeTab === 'healthcare' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <HeartPulse className="w-5 h-5 text-rose-400" />
                <span>Healthcare Discovery & Civic Medical Facilities</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                {healthcare
                  ? `Showing ${healthcare.total} mapped healthcare locations for ${city.name} across hospitals, clinics, dental, and pharmacies.`
                  : 'Grounded OpenStreetMap Overpass medical locations'}
              </p>
            </div>

            <button
              onClick={() => refetchHealth()}
              disabled={isRefetchingHealth}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
              title="Refetch healthcare"
            >
              <RefreshCw className={`w-3 h-3 ${isRefetchingHealth ? 'animate-spin text-indigo-400' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>

          {/* Category Filter Chips */}
          <div className="flex flex-wrap gap-2">
            {HEALTH_FILTER_CATEGORIES.map((cat) => (
              <button
                key={cat.key}
                type="button"
                onClick={() => setSelectedHealthCategory(cat.key)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                  selectedHealthCategory === cat.key
                    ? 'bg-rose-600 text-white shadow-md shadow-rose-600/30'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                <span>{cat.emoji}</span>
                <span>{cat.label}</span>
              </button>
            ))}
          </div>

          {/* Honest Disclaimer */}
          {healthcare?.disclaimer && (
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-400 text-xs">
              <strong>Registry Disclaimer:</strong> {healthcare.disclaimer}
            </div>
          )}

          {/* Facilities Grid */}
          {healthLoading ? (
            <LoadingSkeleton count={4} height="h-28" />
          ) : healthcare?.facilities && healthcare.facilities.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {healthcare.facilities.map((fac) => (
                <div
                  key={fac.facility_id}
                  className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <h4 className="text-sm font-bold text-white line-clamp-1" title={fac.name}>
                        {fac.name}
                      </h4>
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 shrink-0">
                        {fac.type}
                      </span>
                    </div>

                    {fac.address && (
                      <p className="text-xs text-slate-400 line-clamp-2 mt-1">{fac.address}</p>
                    )}

                    {/* Contact & Hours Info */}
                    <div className="mt-2 space-y-1 text-[11px] text-slate-400">
                      {fac.phone && (
                        <div className="flex items-center gap-1.5 text-slate-300">
                          <Phone className="w-3 h-3 text-slate-500" />
                          <span>{fac.phone}</span>
                        </div>
                      )}
                      {fac.opening_hours && (
                        <div className="flex items-center gap-1.5 text-slate-400">
                          <Clock className="w-3 h-3 text-slate-500" />
                          <span>{fac.opening_hours}</span>
                        </div>
                      )}
                      {fac.emergency && (
                        <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-red-500/20 text-red-300 font-bold">
                          Emergency Services Available
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="text-sky-400 font-semibold font-mono">
                      {fac.distance_meters !== undefined && fac.distance_meters !== null
                        ? fac.distance_meters > 1000
                          ? `${(fac.distance_meters / 1000).toFixed(1)} km away`
                          : `${Math.round(fac.distance_meters)}m away`
                        : 'Proximity mapped'}
                    </span>
                    {fac.website ? (
                      <a
                        href={fac.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-1"
                      >
                        <span>Website</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <span className="text-slate-600">No website</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <Building2 className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">No Facilities Recorded for "{selectedHealthCategory}"</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 9: Mobility & Transit */}
      {activeTab === 'transit' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Bus className="w-5 h-5 text-blue-400" />
                <span>Public Transportation & GTFS Registry</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Federated public transit feeds and GTFS-Realtime status.
              </p>
            </div>

            <button
              onClick={() => refetchTransit()}
              disabled={isRefetchingTransit}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
              title="Refetch transit status"
            >
              <RefreshCw className={`w-3 h-3 ${isRefetchingTransit ? 'animate-spin text-indigo-400' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>

          {transitLoading ? (
            <LoadingSkeleton count={2} height="h-28" />
          ) : transit?.transit ? (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800">
              <h4 className="text-sm font-bold text-white mb-2">Registered GTFS Transit Agency</h4>
              <pre className="p-4 rounded-xl bg-slate-900 text-xs text-slate-300 overflow-x-auto font-mono">
                {JSON.stringify(transit.transit, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">GTFS Transit Feed Unavailable</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 10: Multi-Agent Intelligence */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                <span>Multi-Agent Orchestrator Intelligence</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Deterministic synthesis across the 7 specialized domain intelligence agents.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => refetchIntel()}
                disabled={isRefetchingIntel}
                className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium flex items-center gap-1.5 transition-colors"
                title="Re-run orchestrator"
              >
                <RefreshCw className={`w-3 h-3 ${isRefetchingIntel ? 'animate-spin text-indigo-400' : ''}`} />
                <span>Re-run Agents</span>
              </button>
              {intelligence?.overall_status && (
                <StatusBadge status={intelligence.overall_status} label={`Orchestrator: ${intelligence.overall_status}`} />
              )}
            </div>
          </div>

          {intelLoading ? (
            <LoadingSkeleton count={3} height="h-32" />
          ) : intelligence ? (
            <div className="space-y-6">
              {/* Orchestrator Signals */}
              {intelligence.signals && intelligence.signals.length > 0 && (
                <div className="glass-panel p-6 rounded-2xl border border-slate-800">
                  <h4 className="text-sm font-bold text-white mb-3">Domain Signals Extracted</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {intelligence.signals.map((sig, sIdx) => (
                      <div key={sIdx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                        <span className="text-[10px] uppercase font-bold text-indigo-400 block mb-0.5">
                          {sig.domain}
                        </span>
                        <div className="flex justify-between items-center text-slate-200">
                          <span>{sig.metric}</span>
                          <span className="font-semibold text-white font-mono">
                            {typeof sig.value === 'object' ? JSON.stringify(sig.value) : String(sig.value)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Agent Results Breakdown */}
              <div className="space-y-4">
                <h4 className="text-sm font-bold text-white">Agent Output & Provenance</h4>
                {intelligence.results?.map((res, rIdx) => (
                  <div key={rIdx} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-200 font-mono capitalize">
                        {res.agent_id.replace('_', ' ')}
                      </span>
                      <StatusBadge status={res.status} />
                    </div>

                    {res.summary && (
                      <p className="text-xs text-slate-300 leading-relaxed">{res.summary}</p>
                    )}

                    {res.warnings && res.warnings.length > 0 && (
                      <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
                        <strong>Warnings:</strong> {res.warnings.join('; ')}
                      </div>
                    )}

                    {res.sources && res.sources.length > 0 && (
                      <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800">
                        {res.sources.map((s, sIdx) => (
                          <ProvenanceTag
                            key={sIdx}
                            source={s.source_id}
                            confidence={s.confidence}
                            observedAt={s.observed_at}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* RAG Knowledge Evidence Chunks */}
              {intelligence.knowledge_evidence && intelligence.knowledge_evidence.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-white">Retrieved RAG Knowledge Evidence</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {intelligence.knowledge_evidence.map((chunk, cIdx) => (
                      <EvidenceCard key={cIdx} evidence={chunk} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">Orchestrator Execution Not Completed</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
