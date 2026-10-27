import React, { useState } from 'react';
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
} from 'lucide-react';
import {
  useCity,
  useCityWeather,
  useCityAirQuality,
  useCityCost,
  useCityUniversities,
  useCityTransit,
  useCityIntelligence,
} from '../hooks/useUrbanLens';
import { StatusBadge } from '../components/StatusBadge';
import { ProvenanceTag } from '../components/ProvenanceTag';
import { MetricCard } from '../components/MetricCard';
import { EvidenceCard } from '../components/EvidenceCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

type TabKey = 'overview' | 'weather' | 'airQuality' | 'cost' | 'education' | 'transit' | 'agents';

export const CityPage: React.FC = () => {
  const { cityId } = useParams<{ cityId: string }>();
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  // Real backend queries
  const { data: cityData, isLoading: cityLoading, error: cityError } = useCity(cityId || '');
  const { data: weatherData, isLoading: weatherLoading } = useCityWeather(cityId || '');
  const { data: aqiData, isLoading: aqiLoading } = useCityAirQuality(cityId || '');
  const { data: costData, isLoading: costLoading } = useCityCost(cityId || '');
  const { data: uniData, isLoading: uniLoading } = useCityUniversities(cityId || '');
  const { data: transitData, isLoading: transitLoading } = useCityTransit(cityId || '');
  const { data: intelData, isLoading: intelLoading } = useCityIntelligence(cityId || '');

  const city = cityData?.data;
  const weather = weatherData?.data?.weather;
  const weatherMeta = weatherData?.data?.meta;
  const aqi = aqiData?.data;
  const cost = costData?.data;
  const universities = uniData?.data || [];
  const transit = transitData?.data;
  const intelligence = intelData?.data;

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
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-500 transition-colors"
        >
          <Compass className="w-4 h-4" />
          <span>Back to City Explorer</span>
        </Link>
      </div>
    );
  }

  const tabs: { key: TabKey; label: string; icon: React.ReactNode }[] = [
    { key: 'overview', label: 'Overview', icon: <Eye className="w-4 h-4" /> },
    { key: 'weather', label: 'Live Weather', icon: <Thermometer className="w-4 h-4" /> },
    { key: 'airQuality', label: 'Air Quality', icon: <Wind className="w-4 h-4" /> },
    { key: 'cost', label: 'Cost of Living', icon: <Coins className="w-4 h-4" /> },
    { key: 'education', label: 'Universities', icon: <GraduationCap className="w-4 h-4" /> },
    { key: 'transit', label: 'Mobility & Transit', icon: <Bus className="w-4 h-4" /> },
    { key: 'agents', label: 'Multi-Agent Intelligence', icon: <Layers className="w-4 h-4" /> },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* City Header Banner */}
      <section className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {city.country_iso2} • {city.country_id}
              </span>
              <StatusBadge status="database" label="Atlas Canonical Record" />
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
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                {city.latitude.toFixed(4)}°N, {city.longitude.toFixed(4)}°E
              </span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-3">
            <Link
              to={`/compare?city1=${encodeURIComponent(city.city_id)}`}
              className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all flex items-center gap-2"
            >
              <span>Compare</span>
            </Link>
            <Link
              to={`/ask?cityId=${encodeURIComponent(city.city_id)}`}
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-white" />
              <span>Ask AI Intelligence</span>
            </Link>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mt-8 pt-4 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Population"
              value={city.population}
              icon={<Users className="w-4 h-4" />}
              status="database"
              subValue={`Canonical WorldCities Data`}
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
              value={
                aqi?.global_weather?.[0]?.pm25 !== undefined
                  ? aqi.global_weather[0].pm25
                  : (aqi?.who_annual?.[0]?.pm25_annual_mean_ug_m3 ?? aqi?.who_annual?.[0]?.pm25_annual_mean)
              }
              unit="µg/m³"
              icon={<Wind className="w-4 h-4" />}
              status={aqi?.global_weather?.length ? 'fresh' : aqi?.who_annual?.length ? 'database' : 'unavailable'}
              subValue={aqi?.who_annual?.[0] ? `WHO Annual Mean (${aqi.who_annual[0].year})` : 'Global Sensor Data'}
            />
            <MetricCard
              label="Universities Tracked"
              value={universities.length}
              icon={<GraduationCap className="w-4 h-4" />}
              status="database"
              subValue="Ranked Higher Education"
            />
          </div>

          {/* Quick Intelligence Summary Banner */}
          {intelligence?.summary && (
            <div className="glass-panel p-6 rounded-2xl border border-indigo-500/20 bg-indigo-950/20">
              <div className="flex items-center gap-2 mb-2 text-indigo-400 text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-4 h-4" />
                <span>Multi-Agent Synthesized Overview</span>
              </div>
              <p className="text-slate-200 text-sm leading-relaxed">{intelligence.summary}</p>
            </div>
          )}

          {/* Provider Identifiers & Metadata */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-4">Canonical Registry Identifiers</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
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
                <span className="text-slate-500 block mb-1">WorldCities ID</span>
                <span className="font-mono text-slate-200 font-semibold">
                  {city.worldcities_id || 'Canonical'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Live Weather */}
      {activeTab === 'weather' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Thermometer className="w-5 h-5 text-indigo-400" />
              <span>Real-Time Atmospheric Conditions</span>
            </h3>
            {weatherMeta && (
              <ProvenanceTag
                source={weatherMeta.provider || 'Open-Meteo API'}
                observedAt={weatherMeta.observed_at}
                confidence={weatherMeta.confidence}
              />
            )}
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
                          {new Date(df.date).toLocaleDateString(undefined, { weekday: 'short', month: 'numeric', day: 'numeric' })}
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
              <p className="text-xs text-slate-500 mt-1">
                The Open-Meteo live endpoint could not return atmospheric data for this coordinate.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Air Quality */}
      {activeTab === 'airQuality' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Wind className="w-5 h-5 text-teal-400" />
              <span>Air Quality & Environmental Sensor Metrics</span>
            </h3>
            {aqi?.meta && (
              <span className="text-xs text-slate-400">
                Sources: {aqi.meta.sources?.join(', ') || 'Global Sensor Repositories'}
              </span>
            )}
          </div>

          {aqiLoading ? (
            <LoadingSkeleton count={2} height="h-32" />
          ) : aqi && (aqi.global_weather?.length > 0 || aqi.who_annual?.length > 0) ? (
            <div className="space-y-6">
              {/* Sensor Records */}
              {aqi.global_weather?.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <MetricCard
                    label="Air Quality Index"
                    value={aqi.global_weather[0].aqi_us_epa ?? aqi.global_weather[0].air_quality_index}
                    status="fresh"
                    subValue="EPA / Sensor AQI"
                  />
                  <MetricCard
                    label="PM2.5 Concentration"
                    value={aqi.global_weather[0].pm25}
                    unit="µg/m³"
                    status="fresh"
                    subValue="Fine particulate matter"
                  />
                  <MetricCard
                    label="PM10 Concentration"
                    value={aqi.global_weather[0].pm10}
                    unit="µg/m³"
                    status="fresh"
                    subValue="Respirable particulates"
                  />
                  <MetricCard
                    label="Nitrogen Dioxide (NO2)"
                    value={aqi.global_weather[0].no2 ?? aqi.global_weather[0].nitrogen_dioxide}
                    unit="µg/m³"
                    status="fresh"
                    subValue="Combustion emissions"
                  />
                </div>
              )}

              {/* WHO Annual Ambient Air Quality History */}
              {aqi.who_annual && aqi.who_annual.length > 0 && (
                <div className="glass-panel p-6 rounded-2xl border border-slate-800">
                  <h4 className="text-sm font-bold text-white mb-4">
                    WHO Historical Air Quality Standards Benchmark
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left text-slate-300">
                      <thead className="text-[11px] uppercase bg-slate-900/80 text-slate-400">
                        <tr>
                          <th className="py-2.5 px-4 rounded-l-lg">Year</th>
                          <th className="py-2.5 px-4">PM2.5 Annual Mean</th>
                          <th className="py-2.5 px-4">PM10 Annual Mean</th>
                          <th className="py-2.5 px-4 rounded-r-lg">NO2 Annual Mean</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {aqi.who_annual.map((row, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/50">
                            <td className="py-2.5 px-4 font-mono font-bold text-white">{row.year}</td>
                            <td className="py-2.5 px-4">{(row.pm25_annual_mean_ug_m3 ?? row.pm25_annual_mean) ? `${row.pm25_annual_mean_ug_m3 ?? row.pm25_annual_mean} µg/m³` : '—'}</td>
                            <td className="py-2.5 px-4">{(row.pm10_annual_mean_ug_m3 ?? row.pm10_annual_mean) ? `${row.pm10_annual_mean_ug_m3 ?? row.pm10_annual_mean} µg/m³` : '—'}</td>
                            <td className="py-2.5 px-4">{row.no2_annual_mean ? `${row.no2_annual_mean} µg/m³` : '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">No Air Quality Records Registered</p>
              <p className="text-xs text-slate-500 mt-1">
                Neither real-time sensor stations nor WHO annual records are present for this city.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Cost of Living */}
      {activeTab === 'cost' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Coins className="w-5 h-5 text-amber-400" />
              <span>Cost of Living Indices & Consumer Pricing</span>
            </h3>
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
                      <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center text-xs">
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
              <p className="text-xs text-slate-500 mt-1">
                No verified cost or Numbeo consumer basket records exist for this city in MongoDB Atlas.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Education & Universities */}
      {activeTab === 'education' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-purple-400" />
              <span>Higher Education & Ranked Universities</span>
            </h3>
            <span className="text-xs text-slate-400">Total: {universities.length} Institutions</span>
          </div>

          {uniLoading ? (
            <LoadingSkeleton count={3} height="h-24" />
          ) : universities.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {universities.map((uni) => (
                <div
                  key={uni.university_id}
                  className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h4 className="text-base font-bold text-white">{uni.name}</h4>
                      {uni.website && (
                        <a
                          href={uni.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1"
                        >
                          <span>Website</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                    <span className="text-xs text-slate-500 font-mono">
                      ID: {uni.university_id} • {uni.country_iso2}
                    </span>
                  </div>

                  {uni.rankings && uni.rankings.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap gap-2">
                      {uni.rankings.map((r, rIdx) => (
                        <span
                          key={rIdx}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-purple-500/10 text-purple-300 border border-purple-500/20"
                        >
                          <span className="font-semibold">{r.ranking_metric}:</span>
                          <span>#{r.rank} ({r.ranking_year})</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center glass-panel rounded-2xl border border-slate-800">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
              <p className="text-sm text-slate-300 font-medium">No Universities Indexed for this City</p>
              <p className="text-xs text-slate-500 mt-1">
                No ranked academic institutions are mapped directly to this city slug in MongoDB.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 6: Mobility & Transit */}
      {activeTab === 'transit' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Bus className="w-5 h-5 text-blue-400" />
              <span>Public Transportation & GTFS Status</span>
            </h3>
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
              <p className="text-xs text-slate-500 mt-1">
                No active GTFS or GTFS-Realtime agency feed is registered in the public transit repository for this city.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 7: Multi-Agent Intelligence Orchestrator */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              <span>Multi-Agent Orchestrator Intelligence</span>
            </h3>
            {intelligence?.overall_status && (
              <StatusBadge status={intelligence.overall_status} label={`Orchestrator: ${intelligence.overall_status}`} />
            )}
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
