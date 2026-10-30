import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useUrban } from '../context/UrbanContext';
import { useOriginDestination } from '../context/OriginDestinationContext';
import {
  useCity,
  useCityWeather,
  useCityAirQualityLive,
  useCityCost,
  useCityEducation,
  useCityHealthcare,
  useCurrencyConversion,
  useCityIntelligence
} from '../hooks/useUrbanLens';
import { CityMapCanvas } from '../components/common/CityMapCanvas';
import { DataTrustBadge } from '../components/common/DataTrustBadge';
import {
  Users,
  Wind,
  Thermometer,
  Coins,
  GraduationCap,
  ArrowLeft,
  Sparkles,
  Building2,
  HeartPulse,
  ArrowRightLeft,
  ExternalLink,
  MapPin
} from 'lucide-react';

type TabType = 'overview' | 'environment' | 'education' | 'healthcare' | 'economy' | 'relocation' | 'ai';

export const CityDetailPage: React.FC = () => {
  const { cityId: urlCityId } = useParams<{ cityId: string }>();
  const navigate = useNavigate();
  const { activeCityId, setActiveCityId, toggleAiModal } = useUrban();
  const { origin, setDestination, openOriginModal } = useOriginDestination();

  const cityId = urlCityId || activeCityId;

  // Sync active city if coming from direct URL
  useEffect(() => {
    if (urlCityId && urlCityId !== activeCityId) {
      setActiveCityId(urlCityId);
    }
  }, [urlCityId, activeCityId, setActiveCityId]);

  const [activeTab, setActiveTab] = useState<TabType>('overview');

  // Real Backend Queries
  const { data: cityResp } = useCity(cityId);
  const { data: weatherResp } = useCityWeather(cityId);
  const { data: aqiResp } = useCityAirQualityLive(cityId);
  const { data: costResp } = useCityCost(cityId);
  const { data: eduResp } = useCityEducation(cityId);
  const { data: healthResp } = useCityHealthcare(cityId);
  const { data: intelResp } = useCityIntelligence(cityId);

  const city = cityResp?.data;
  const weather = weatherResp?.data?.weather?.current;
  const forecasts = weatherResp?.data?.weather?.daily_forecasts || [];
  const aqiPollutants = aqiResp?.data?.air_quality?.pollutants;
  const costSummary = costResp?.data?.summary;
  const institutions = eduResp?.data?.institutions || [];
  const facilities = healthResp?.data?.facilities || [];
  const agents = intelResp?.data?.results || [];

  // Update Relocation Destination
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

  // Live Currency Conversion (Origin -> Destination)
  const baseCurrency = origin.currency_code || 'INR';
  const destCurrency = city?.currency?.code || 'USD';
  const { data: fxResp } = useCurrencyConversion(baseCurrency, destCurrency, 100000);
  const fx = fxResp?.data;

  const tempVal = weather?.temperature_c !== undefined && weather?.temperature_c !== null ? Math.round(weather.temperature_c) : null;
  const pm25 = aqiPollutants?.pm25;
  const aqiVal = pm25 ? Math.round(pm25 * 2.1) : null;
  const costIdx = costSummary?.consumer_price_index ?? null;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/80 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6 shadow-xl">
        <div>
          <button
            onClick={() => navigate('/app/explore')}
            className="text-xs font-mono text-slate-400 hover:text-white flex items-center gap-1.5 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>RETURN TO CITY EXPLORER</span>
          </button>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl sm:text-4xl font-black font-display text-white tracking-tight uppercase">
              {city?.name || 'Loading City...'} · {city?.country_iso2}
            </h1>
            <DataTrustBadge status="LIVE" size="md" source="Canonical Registry & Live Telemetry" />
          </div>
          <p className="text-xs sm:text-sm text-slate-300 font-mono mt-1">
            COORDINATES: {city ? `${city.latitude.toFixed(4)}° N, ${city.longitude.toFixed(4)}° E` : 'Syncing...'} · ADMIN: {city?.admin_name || 'Metropolitan'}
          </p>
        </div>

        <button
          onClick={() => toggleAiModal(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-xs tracking-wider transition-all shadow-[0_0_20px_rgba(34,211,238,0.25)] flex items-center gap-1.5 self-start md:self-auto"
        >
          <Sparkles className="w-4 h-4" />
          <span>ASK AI ABOUT {city?.name?.toUpperCase() || 'THIS CITY'}</span>
        </button>
      </div>

      {/* Quick Intelligence Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Users className="w-3 h-3 text-cyan-400" /> POPULATION
          </span>
          <div className="text-base font-bold font-mono text-white mt-1 truncate">
            {city?.population ? city.population.toLocaleString() : 'Not recorded'}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Thermometer className="w-3 h-3 text-amber-400" /> TEMPERATURE
          </span>
          <div className="text-base font-bold font-mono text-cyan-400 mt-1">
            {tempVal !== null ? `${tempVal}°C` : 'Syncing'}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Wind className="w-3 h-3 text-purple-400" /> AIR QUALITY
          </span>
          <div className="text-base font-bold font-mono text-purple-400 mt-1">
            {aqiVal !== null ? `AQI ${aqiVal}` : 'Syncing'}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <GraduationCap className="w-3 h-3 text-emerald-400" /> HIGHER ED
          </span>
          <div className="text-base font-bold font-mono text-emerald-400 mt-1">
            {institutions.length > 0 ? `${institutions.length} Institutions` : 'Querying'}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Coins className="w-3 h-3 text-amber-400" /> COST INDEX
          </span>
          <div className="text-base font-bold font-mono text-white mt-1 truncate">
            {costIdx !== null ? `${costIdx} (NYC=100)` : 'No Data'}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <ArrowRightLeft className="w-3 h-3 text-blue-400" /> CURRENCY
          </span>
          <div className="text-base font-bold font-mono text-white mt-1 truncate">
            {city?.currency?.code || 'USD'} ({city?.currency?.symbol || '$'})
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-[#1E334A] pb-1 overflow-x-auto scrollbar-none">
        {[
          { id: 'overview', label: 'Overview' },
          { id: 'environment', label: 'Environment & Weather' },
          { id: 'education', label: 'Education' },
          { id: 'healthcare', label: 'Healthcare' },
          { id: 'economy', label: 'Cost & Economy' },
          { id: 'relocation', label: 'Relocation FX' },
          { id: 'ai', label: 'AI Intelligence' },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as TabType)}
            className={`px-4 py-2 text-xs font-mono font-semibold transition-colors border-b-2 whitespace-nowrap ${
              activeTab === t.id
                ? 'border-cyan-400 text-cyan-300'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">
                ACTIVE DIGITAL TWIN VECTOR CANVASES
              </h2>
              <DataTrustBadge status="LIVE" size="sm" source="OpenStreetMap Overpass" />
            </div>
            <CityMapCanvas cityId={cityId} heightClass="h-[480px]" />
          </div>

          {/* Quick Context Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-4">
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
                <Building2 className="w-4 h-4 text-cyan-400" />
                METROPOLITAN PROFILE
              </h3>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between py-1.5 border-b border-[#1E334A]/50">
                  <span className="text-slate-400">CANONICAL CITY ID</span>
                  <span className="text-white">{city?.city_id || cityId}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#1E334A]/50">
                  <span className="text-slate-400">ADMINISTRATIVE PROVINCE</span>
                  <span className="text-white">{city?.admin_name || 'Standard'}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-[#1E334A]/50">
                  <span className="text-slate-400">CAPITAL STATUS</span>
                  <span className="text-emerald-400">{city?.capital ? `Yes (${city.capital})` : 'No'}</span>
                </div>
                <div className="flex justify-between py-1.5">
                  <span className="text-slate-400">CURRENCY</span>
                  <span className="text-cyan-400">{city?.currency?.name} ({city?.currency?.code})</span>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-4">
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
                <ArrowRightLeft className="w-4 h-4 text-blue-400" />
                RELOCATION CORRIDOR
              </h3>
              <div className="space-y-3 text-xs font-mono">
                <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A]">
                  <div className="text-[10px] text-slate-400">CURRENT ORIGIN</div>
                  <div className="text-sm font-bold text-white mt-0.5">{origin.city_name}, {origin.country_name}</div>
                  <button
                    onClick={openOriginModal}
                    className="text-[10px] text-cyan-400 hover:underline mt-1 block"
                  >
                    Change Origin City →
                  </button>
                </div>
                <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A]">
                  <div className="text-[10px] text-slate-400">DESTINATION</div>
                  <div className="text-sm font-bold text-emerald-400 mt-0.5">{city?.name}, {city?.country_iso2}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Environment & Weather */}
      {activeTab === 'environment' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
              <span className="text-xs font-mono text-slate-400">TEMPERATURE</span>
              <div className="text-3xl font-extrabold font-mono text-white mt-1">
                {tempVal !== null ? `${tempVal}°C` : 'N/A'}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-1">
                Feels like {weather?.apparent_temperature_c ? `${Math.round(weather.apparent_temperature_c)}°C` : 'N/A'}
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
              <span className="text-xs font-mono text-slate-400">AIR QUALITY (AQI)</span>
              <div className="text-3xl font-extrabold font-mono text-purple-400 mt-1">
                {aqiVal !== null ? `AQI ${aqiVal}` : 'N/A'}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-1">
                PM2.5: {pm25 ? `${pm25.toFixed(1)} µg/m³` : 'N/A'}
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
              <span className="text-xs font-mono text-slate-400">HUMIDITY</span>
              <div className="text-3xl font-extrabold font-mono text-white mt-1">
                {weather?.relative_humidity_pct ? `${weather.relative_humidity_pct}%` : 'N/A'}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-1">
                Pressure: {weather?.surface_pressure_mb ? `${Math.round(weather.surface_pressure_mb)} hPa` : 'N/A'}
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
              <span className="text-xs font-mono text-slate-400">WIND SPEED</span>
              <div className="text-3xl font-extrabold font-mono text-cyan-400 mt-1">
                {weather?.wind_speed_kph ? `${Math.round(weather.wind_speed_kph)} km/h` : 'N/A'}
              </div>
              <div className="text-xs text-slate-400 font-mono mt-1">
                Condition: {weather?.condition || 'Normal'}
              </div>
            </div>
          </div>

          {/* 5-Day Forecast */}
          {forecasts.length > 0 && (
            <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-4">
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                5-DAY METEOROLOGICAL FORECAST
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
                {forecasts.map((fc, i) => (
                  <div key={i} className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] text-center space-y-1">
                    <div className="text-[10px] font-mono text-slate-400">{fc.date}</div>
                    <div className="text-lg font-bold font-mono text-white">
                      {fc.temp_max_c ? `${Math.round(fc.temp_max_c)}°` : '--'} / {fc.temp_min_c ? `${Math.round(fc.temp_min_c)}°` : '--'}
                    </div>
                    <div className="text-[11px] font-mono text-cyan-400 truncate">{fc.condition || 'Clear'}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Education */}
      {activeTab === 'education' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
              HIGHER EDUCATION INSTITUTIONS ({institutions.length})
            </h2>
            <DataTrustBadge status="VERIFIED" size="sm" source="Canonical Education Registry" />
          </div>

          {institutions.length === 0 ? (
            <div className="p-8 rounded-2xl bg-[#0B1726] border border-[#1E334A] text-center text-xs font-mono text-slate-400">
              No accredited higher education institutions registered in immediate municipal boundary.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {institutions.map((inst) => (
                <div key={inst.institution_id} className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-sm font-bold font-mono text-white">{inst.name}</h4>
                      <span className="text-[11px] font-mono text-purple-300">{inst.type}</span>
                    </div>
                    {inst.website && (
                      <a
                        href={inst.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 p-1"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                  {inst.address && (
                    <div className="text-xs font-mono text-slate-400 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      <span className="truncate">{inst.address}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Healthcare */}
      {activeTab === 'healthcare' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
              HEALTHCARE INFRASTRUCTURE ({facilities.length})
            </h2>
            <DataTrustBadge status="LIVE" size="sm" source="OpenStreetMap Overpass" />
          </div>

          {facilities.length === 0 ? (
            <div className="p-8 rounded-2xl bg-[#0B1726] border border-[#1E334A] text-center text-xs font-mono text-slate-400">
              Querying municipal hospitals and clinics...
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {facilities.map((fac) => (
                <div key={fac.facility_id} className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-sm font-bold font-mono text-white">{fac.name}</h4>
                      <span className="text-[11px] font-mono text-emerald-400 uppercase">{fac.type || fac.amenity || 'Facility'}</span>
                    </div>
                    <HeartPulse className="w-4 h-4 text-rose-400" />
                  </div>
                  {fac.address && (
                    <div className="text-xs font-mono text-slate-400 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      <span className="truncate">{fac.address}</span>
                    </div>
                  )}
                  {fac.distance_meters && (
                    <div className="text-[10px] font-mono text-slate-400">
                      DISTANCE: {(fac.distance_meters / 1000).toFixed(1)} km from urban core
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 5: Economy & Cost */}
      {activeTab === 'economy' && (
        <div className="space-y-6">
          {costIdx === null ? (
            <div className="p-12 rounded-3xl bg-[#0B1726] border border-rose-500/30 text-center max-w-2xl mx-auto space-y-4">
              <h2 className="text-lg font-bold font-mono text-white uppercase tracking-wider">
                COST INTELLIGENCE UNAVAILABLE
              </h2>
              <p className="text-xs text-slate-300 font-mono">
                UrbanLens does not currently have verified city-level cost data for {city?.name}.
                <br />No estimated or fabricated value is being displayed.
              </p>
              <DataTrustBadge status="DATA UNAVAILABLE" size="md" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
                <span className="text-xs font-mono text-slate-400">CONSUMER PRICE INDEX</span>
                <div className="text-3xl font-extrabold font-mono text-white">{costIdx}</div>
                <div className="text-xs font-mono text-slate-400">Baseline New York City = 100.0</div>
              </div>

              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
                <span className="text-xs font-mono text-slate-400">RENT INDEX</span>
                <div className="text-3xl font-extrabold font-mono text-cyan-400">{costSummary?.rent_index ?? 'N/A'}</div>
                <div className="text-xs font-mono text-slate-400">Relative rental market burden</div>
              </div>

              <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
                <span className="text-xs font-mono text-slate-400">PURCHASING POWER</span>
                <div className="text-3xl font-extrabold font-mono text-emerald-400">{costSummary?.purchasing_power_index ?? 'N/A'}</div>
                <div className="text-xs font-mono text-slate-400">Local salary purchasing power</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 6: Relocation FX */}
      {activeTab === 'relocation' && (
        <div className="space-y-6">
          <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                CURRENCY & RELOCATION TRANSLATION MATRIX
              </h3>
              <DataTrustBadge status="LIVE" size="sm" source={fx?.provider || 'Frankfurter ECB'} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-2">
                <span className="text-[10px] font-mono text-slate-400">ORIGIN BUDGET</span>
                <div className="text-2xl font-black font-mono text-white">
                  100,000 {baseCurrency}
                </div>
                <div className="text-xs font-mono text-slate-400">Standard monthly benchmark allocation</div>
              </div>

              <div className="p-5 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-2">
                <span className="text-[10px] font-mono text-slate-400">DESTINATION CONVERSION</span>
                <div className="text-2xl font-black font-mono text-emerald-400">
                  {fx?.converted_amount ? `${city?.currency?.symbol || ''}${Math.round(fx.converted_amount).toLocaleString()} ${destCurrency}` : 'Syncing'}
                </div>
                <div className="text-xs font-mono text-slate-400">
                  1 {baseCurrency} = {fx?.rate ? fx.rate.toFixed(4) : '--'} {destCurrency}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 7: AI Intelligence */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
              MULTI-AGENT INTELLIGENCE RESULTS
            </h2>
            <button
              onClick={() => toggleAiModal(true)}
              className="px-3 py-1.5 rounded-lg bg-cyan-950 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-semibold"
            >
              Ask Custom Question
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {agents.map((ag) => (
              <div key={ag.agent_id} className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-white uppercase">{ag.agent_id}</span>
                  <span className="text-[10px] font-mono text-emerald-400 font-bold">{Math.round(ag.confidence * 100)}% CONF</span>
                </div>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">{ag.summary || ag.detail || 'Telemetry nominal.'}</p>
                {ag.knowledge_evidence && ag.knowledge_evidence.length > 0 && (
                  <div className="pt-2 border-t border-[#1E334A] text-[10px] font-mono text-cyan-400">
                    Citations: {ag.knowledge_evidence.length} Authoritative documents
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
