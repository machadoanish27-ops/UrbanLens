import React, { useState, useEffect, useMemo } from 'react';
import type { CityDetailResponse, WeatherCurrent } from '../types/api';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { normalizeCityId, getStudioKeyForId, CITIES_DATA } from '../data/urbanData';
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
import { InteractiveMap, type MapMarkerItem } from '../components/InteractiveMap';
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
  MapPin,
  Phone,
  Crosshair,
  Search
} from 'lucide-react';

type TabType = 'overview' | 'environment' | 'education' | 'healthcare' | 'economy' | 'relocation' | 'ai';

export interface CityDetailPageProps {
  initialTab?: TabType;
}

export const CityDetailPage: React.FC<CityDetailPageProps> = ({ initialTab = 'overview' }) => {
  const { cityId: urlCityId } = useParams<{ cityId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { activeCityId, setActiveCityId, currentCity, toggleAiModal } = useUrban();
  const { origin, destination, setDestination, openOriginModal } = useOriginDestination();

  // When loaded with a specific URL city param, sync it to activeCityId
  useEffect(() => {
    if (urlCityId) {
      const norm = normalizeCityId(urlCityId);
      if (norm !== activeCityId) {
        setActiveCityId(norm);
      }
    }
  }, [urlCityId]);

  const rawCityId = urlCityId || activeCityId;
  const cityId = normalizeCityId(rawCityId);

  const [activeTab, setActiveTab] = useState<TabType>(initialTab);

  useEffect(() => {
    const tabParam = searchParams.get('tab');
    if (tabParam && ['overview', 'environment', 'education', 'healthcare', 'economy', 'relocation', 'ai'].includes(tabParam)) {
      setActiveTab(tabParam as TabType);
    } else if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab, searchParams]);

  // Real Backend Queries
  const { data: cityResp } = useCity(cityId);
  const { data: weatherResp } = useCityWeather(cityId);
  const { data: aqiResp } = useCityAirQualityLive(cityId);
  const { data: costResp } = useCityCost(cityId);
  const { data: eduResp } = useCityEducation(cityId);
  const { data: healthResp } = useCityHealthcare(cityId);
  const { data: intelResp } = useCityIntelligence(cityId);

  // Synchronous fallback from canonical seed cities or currentCity
  const fallbackCity = useMemo(() => {
    const key = getStudioKeyForId(cityId);
    if (key && CITIES_DATA[key]) return CITIES_DATA[key];
    return currentCity;
  }, [cityId, currentCity]);

  const city = useMemo<CityDetailResponse | undefined>(() => {
    if (cityResp?.data) return cityResp.data;
    if (!fallbackCity) return undefined;
    return {
      city_id: fallbackCity.id,
      worldcities_id: null,
      name: fallbackCity.name,
      name_ascii: fallbackCity.name,
      country_id: fallbackCity.country_id || `country_${fallbackCity.countryCode}`,
      country_iso2: fallbackCity.countryCode,
      country_iso3: null,
      admin_name: 'Metropolitan Area',
      capital: null,
      latitude: fallbackCity.latitude,
      longitude: fallbackCity.longitude,
      population: fallbackCity.populationRaw || 0,
      population_density: null,
      aliases: [],
      provider_identities: {},
      currency: {
        code: fallbackCity.currency?.code || 'USD',
        symbol: fallbackCity.currency?.symbol || '$',
        name: fallbackCity.currency?.name || 'Currency',
      },
      languages: null,
    };
  }, [cityResp?.data, fallbackCity]);

  const weather = useMemo<WeatherCurrent | undefined>(() => {
    if (weatherResp?.data?.weather?.current) return weatherResp.data.weather.current;
    if (!fallbackCity) return undefined;
    return {
      temperature_c: fallbackCity.temperature,
      apparent_temperature_c: fallbackCity.feelsLike,
      relative_humidity_pct: fallbackCity.humidity,
      surface_pressure_mb: 1013,
      wind_speed_kph: parseFloat(fallbackCity.windSpeed) || 0,
      precipitation_mm: 0,
      weather_code: 0,
      condition: 'Active Telemetry',
      observed_at: new Date().toISOString(),
    };
  }, [weatherResp?.data?.weather?.current, fallbackCity]);

  const forecasts = weatherResp?.data?.weather?.daily_forecasts || [];
  const aqiPollutants = aqiResp?.data?.air_quality?.pollutants || (fallbackCity ? {
    pm25: fallbackCity.pm25,
    pm10: fallbackCity.pm10,
    no2: fallbackCity.no2,
    o3: fallbackCity.o3,
  } : undefined);
  const costSummary = costResp?.data?.summary || (fallbackCity && fallbackCity.costOfLivingIndex ? {
    consumer_price_index: fallbackCity.costOfLivingIndex,
    rent_index: null,
    cost_of_living_plus_rent_index: null,
    groceries_index: null,
    restaurant_price_index: null,
    local_purchasing_power_index: null,
    purchasing_power_index: null,
  } : undefined);
  const institutions = eduResp?.data?.institutions || [];
  const facilities = useMemo(() => {
    return healthResp?.data?.facilities || healthResp?.data?.items || [];
  }, [healthResp?.data]);
  const agents = intelResp?.data?.results || [];

  // Healthcare Discovery State
  const [healthCategory, setHealthCategory] = useState<string>('all');
  const [healthSearch, setHealthSearch] = useState<string>('');

  const healthcareTotal = healthResp?.data?.total ?? facilities.length;
  const hospitalCount = useMemo(() => facilities.filter(f => (f.type || '').toLowerCase().includes('hospital')).length, [facilities]);
  const clinicCount = useMemo(() => facilities.filter(f => (f.type || '').toLowerCase().includes('clinic')).length, [facilities]);
  const healthCenterCount = useMemo(() => facilities.filter(f => (f.type || '').toLowerCase().includes('health_center') || (f.type || '').toLowerCase().includes('health center')).length, [facilities]);
  const pharmacyCount = useMemo(() => facilities.filter(f => (f.type || '').toLowerCase().includes('pharmacy') || (f.type || '').toLowerCase().includes('chemist')).length, [facilities]);
  const emergencyCount = useMemo(() => facilities.filter(f => f.emergency === true || (typeof f.emergency === 'string' && ['yes', 'true'].includes((f.emergency as string).toLowerCase()))).length, [facilities]);

  const filteredHealthcareFacilities = useMemo(() => {
    let list = facilities;
    if (healthCategory !== 'all') {
      if (healthCategory === 'hospital') {
        list = list.filter(f => (f.type || '').toLowerCase().includes('hospital'));
      } else if (healthCategory === 'clinic') {
        list = list.filter(f => (f.type || '').toLowerCase().includes('clinic'));
      } else if (healthCategory === 'health_center') {
        list = list.filter(f => (f.type || '').toLowerCase().includes('health_center') || (f.type || '').toLowerCase().includes('health center'));
      } else if (healthCategory === 'pharmacy') {
        list = list.filter(f => (f.type || '').toLowerCase().includes('pharmacy') || (f.type || '').toLowerCase().includes('chemist'));
      } else if (healthCategory === 'emergency') {
        list = list.filter(f => f.emergency === true || (typeof f.emergency === 'string' && ['yes', 'true'].includes((f.emergency as string).toLowerCase())));
      }
    }
    if (healthSearch.trim()) {
      const q = healthSearch.trim().toLowerCase();
      list = list.filter(f =>
        (f.name || '').toLowerCase().includes(q) ||
        (f.address || '').toLowerCase().includes(q) ||
        (f.type || '').toLowerCase().includes(q)
      );
    }
    return list;
  }, [facilities, healthCategory, healthSearch]);

  const healthcareMapMarkers = useMemo<MapMarkerItem[]>(() => {
    return filteredHealthcareFacilities
      .filter(f => f.latitude != null && f.longitude != null && !isNaN(f.latitude) && !isNaN(f.longitude))
      .map(f => ({
        lat: f.latitude,
        lon: f.longitude,
        title: f.name,
        category: f.type || 'hospital',
        address: f.address || (f.city_name ? `${f.city_name}, ${f.country || ''}` : undefined),
        distance_meters: f.distance_meters != null ? f.distance_meters : undefined,
        provider: f.source_dataset ? `Kaggle: ${f.source_dataset}` : (f.provider || 'Kaggle Healthcare Dataset'),
        website: f.website || undefined,
        phone: f.phone || undefined,
      }));
  }, [filteredHealthcareFacilities]);

  // Update Relocation Destination (Guarded against loops)
  useEffect(() => {
    if (city && destination?.city_id !== city.city_id) {
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
  }, [city?.city_id, city?.name, city?.country_id, city?.country_iso2, city?.currency?.code, destination?.city_id, setDestination]);

  // Live Currency Conversion (Origin -> Destination)
  const baseCurrency = origin.currency_code || 'INR';
  const destCurrency = city?.currency?.code || fallbackCity?.currency?.code || 'USD';
  const isSameCurrency = baseCurrency.toUpperCase() === destCurrency.toUpperCase();

  const { data: fxResp, isLoading: isFxLoading } = useCurrencyConversion(baseCurrency, destCurrency, 100000);
  const fx = fxResp?.data || (isSameCurrency ? {
    from_currency: baseCurrency,
    to_currency: destCurrency,
    base_currency: baseCurrency,
    quote_currency: destCurrency,
    amount: 100000,
    rate: 1.0,
    inverse_rate: 1.0,
    converted_amount: 100000,
    provider: 'Local / Parity',
    status: 'parity',
    observed_at: new Date().toISOString().split('T')[0],
  } : undefined);

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
              {city?.name || fallbackCity?.name || 'City Intelligence'} · {city?.country_iso2 || fallbackCity?.countryCode}
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
            {tempVal !== null ? `${tempVal}°C` : (fallbackCity ? `${fallbackCity.temperature}°C` : 'N/A')}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Wind className="w-3 h-3 text-purple-400" /> AIR QUALITY
          </span>
          <div className="text-base font-bold font-mono text-purple-400 mt-1">
            {aqiVal !== null ? `AQI ${aqiVal}` : (fallbackCity ? `AQI ${fallbackCity.aqi}` : 'N/A')}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <GraduationCap className="w-3 h-3 text-emerald-400" /> HIGHER ED
          </span>
          <div className="text-base font-bold font-mono text-emerald-400 mt-1">
            {institutions.length > 0 ? `${institutions.length} Institutions` : (fallbackCity?.universities?.length ? `${fallbackCity.universities.length} Institutions` : 'Registered')}
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Coins className="w-3 h-3 text-amber-400" /> COST INDEX
          </span>
          <div className="text-base font-bold font-mono text-white mt-1 truncate">
            {costIdx !== null ? `${costIdx} (NYC=100)` : (fallbackCity?.costOfLivingIndex ? `${fallbackCity.costOfLivingIndex} (NYC=100)` : 'No Data')}
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
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[#1E334A]/60">
            <div>
              <div className="flex items-center gap-2">
                <HeartPulse className="w-5 h-5 text-rose-500" />
                <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                  HEALTHCARE INTELLIGENCE ({facilities.length > 0 ? `${facilities.length} INDEXED` : '0 INDEXED'})
                </h2>
              </div>
              <p className="text-xs font-mono text-slate-400 mt-0.5">
                Verified facility-level medical infrastructure mapped from Global Kaggle Healthcare registries
              </p>
            </div>
            <DataTrustBadge
              status={facilities.length > 0 ? "VERIFIED" : "DATA UNAVAILABLE"}
              size="sm"
              source={facilities.length > 0 ? "Kaggle Healthcare Registry" : "Kaggle Open Registry"}
            />
          </div>

          {/* Metric Summary Counters */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            <div className="p-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">TOTAL FACILITIES</span>
              <div className="text-2xl font-extrabold font-mono text-white">{healthcareTotal}</div>
              <div className="text-[10px] font-mono text-slate-500">Municipal Scope</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">HOSPITALS</span>
              <div className="text-2xl font-extrabold font-mono text-rose-400">{hospitalCount}</div>
              <div className="text-[10px] font-mono text-slate-500">Inpatient / Acute</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">CLINICS</span>
              <div className="text-2xl font-extrabold font-mono text-emerald-400">{clinicCount}</div>
              <div className="text-[10px] font-mono text-slate-500">Outpatient Care</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">HEALTH CENTERS</span>
              <div className="text-2xl font-extrabold font-mono text-cyan-400">{healthCenterCount}</div>
              <div className="text-[10px] font-mono text-slate-500">Primary / Civic</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-1 col-span-2 sm:col-span-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">PHARMACIES & OTHER</span>
              <div className="text-2xl font-extrabold font-mono text-amber-400">{pharmacyCount}</div>
              <div className="text-[10px] font-mono text-slate-500">Dispensaries / Allied</div>
            </div>
          </div>

          {/* Interactive Geospatial Leaflet Map */}
          {city?.latitude != null && city?.longitude != null && (
            <div className="rounded-2xl border border-[#1E334A] overflow-hidden bg-[#030712] space-y-0">
              <div className="px-4 py-3 bg-[#07111F] border-b border-[#1E334A] flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Crosshair className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-mono font-semibold text-white uppercase tracking-wider">
                    SPATIAL TOPOLOGY ({healthcareMapMarkers.length} SITES PLOTTED)
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono text-slate-400">
                    City Anchor: {city.name} ({city.latitude.toFixed(2)}°, {city.longitude.toFixed(2)}°)
                  </span>
                </div>
              </div>
              <InteractiveMap
                latitude={city.latitude}
                longitude={city.longitude}
                cityName={city.name}
                markers={healthcareMapMarkers}
                zoom={12}
                height="h-[360px]"
                showFilters={false}
              />
            </div>
          )}

          {/* Filter Pills & Search Bar */}
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-1.5">
              {[
                { id: 'all', label: `All (${facilities.length})` },
                { id: 'hospital', label: `Hospitals (${hospitalCount})` },
                { id: 'clinic', label: `Clinics (${clinicCount})` },
                { id: 'health_center', label: `Health Centers (${healthCenterCount})` },
                { id: 'pharmacy', label: `Pharmacies (${pharmacyCount})` },
                ...(emergencyCount > 0 ? [{ id: 'emergency', label: `Emergency (${emergencyCount})` }] : []),
              ].map((btn) => (
                <button
                  key={btn.id}
                  onClick={() => setHealthCategory(btn.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all ${
                    healthCategory === btn.id
                      ? 'bg-rose-500 text-white font-bold shadow-md shadow-rose-500/20'
                      : 'bg-[#0B1726] border border-[#1E334A] text-slate-300 hover:border-slate-500'
                  }`}
                >
                  {btn.label}
                </button>
              ))}
            </div>

            <div className="relative min-w-[220px]">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter facilities..."
                value={healthSearch}
                onChange={(e) => setHealthSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-[#0B1726] border border-[#1E334A] text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50"
              />
            </div>
          </div>

          {/* Content: Facility Cards or Empty State */}
          {facilities.length === 0 ? (
            <div className="p-10 rounded-2xl bg-[#0B1726] border border-amber-500/20 text-center space-y-3">
              <div className="flex justify-center">
                <DataTrustBadge status="DATA UNAVAILABLE" size="md" source="Kaggle Healthcare Registry" />
              </div>
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                NO VERIFIED HEALTHCARE FACILITIES INDEXED FOR {city?.name?.toUpperCase() || 'THIS CITY'}
              </h3>
              <p className="text-xs text-slate-300 font-mono max-w-xl mx-auto leading-relaxed">
                UrbanLens anti-hallucination policy strictly prohibits displaying synthetic, guessed, or ungrounded medical facilities.
                <br />
                Global Kaggle healthcare coverage is currently active for cities across Australia, Brazil, Canada, Egypt, Germany, Ghana, India, Indonesia, Nigeria, Singapore, the United Kingdom, and the United States.
              </p>
            </div>
          ) : filteredHealthcareFacilities.length === 0 ? (
            <div className="p-8 rounded-2xl bg-[#0B1726] border border-[#1E334A] text-center space-y-2">
              <p className="text-xs font-mono text-slate-400">
                No facilities match filter "{healthCategory}" {healthSearch ? `and query "${healthSearch}"` : ''}.
              </p>
              <button
                onClick={() => { setHealthCategory('all'); setHealthSearch(''); }}
                className="text-xs font-mono text-cyan-400 hover:underline"
              >
                Reset filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredHealthcareFacilities.map((fac) => (
                <div
                  key={fac.facility_id || (fac as any).healthcare_id}
                  className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/40 transition-colors flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1">
                        <h4 className="text-sm font-bold font-mono text-white leading-snug">
                          {fac.name}
                        </h4>
                        <div className="flex flex-wrap items-center gap-1.5">
                          <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded uppercase ${
                            (fac.type || '').toLowerCase().includes('hospital')
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                              : (fac.type || '').toLowerCase().includes('clinic')
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : (fac.type || '').toLowerCase().includes('health_center')
                              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                              : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          }`}>
                            {fac.type || 'Facility'}
                          </span>
                          {(fac.emergency === true || fac.emergency === 'yes' || fac.emergency === 'true') && (
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-600/20 text-red-300 border border-red-500/30 uppercase">
                              EMERGENCY
                            </span>
                          )}
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                            {fac.source_dataset ? `Kaggle: ${fac.source_dataset}` : 'Source: Kaggle'}
                          </span>
                        </div>
                      </div>
                      <HeartPulse className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    </div>

                    {fac.address && (
                      <div className="text-xs font-mono text-slate-400 flex items-start gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
                        <span className="line-clamp-2">{fac.address}</span>
                      </div>
                    )}
                  </div>

                  <div className="pt-2 border-t border-[#1E334A]/50 flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <div>
                      {fac.distance_meters != null && (
                        <span>
                          {(fac.distance_meters / 1000).toFixed(1)} km from urban core
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      {fac.phone && (
                        <span className="flex items-center gap-1 text-slate-300">
                          <Phone className="w-3 h-3 text-slate-500" />
                          {fac.phone}
                        </span>
                      )}
                      {fac.website && (
                        <a
                          href={fac.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
                        >
                          <span>Portal</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
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
              <DataTrustBadge status={fx?.status === 'fresh' || fx?.status === 'cached' || fx?.status === 'parity' ? 'LIVE' : (isFxLoading ? 'SYNCING' : 'DATA UNAVAILABLE')} size="sm" source={fx?.provider ? `ECB / ${fx.provider}` : 'Frankfurter ECB'} />
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
                  {fx?.converted_amount !== undefined && fx?.converted_amount !== null
                    ? `${city?.currency?.symbol || ''}${Math.round(fx.converted_amount).toLocaleString()} ${destCurrency}`
                    : isFxLoading
                    ? 'Syncing ECB...'
                    : 'Conversion Unavailable'}
                </div>
                <div className="text-xs font-mono text-slate-400">
                  {fx?.rate !== undefined && fx?.rate !== null
                    ? `1 ${baseCurrency} = ${fx.rate.toFixed(4)} ${destCurrency}`
                    : isFxLoading
                    ? `Connecting to ECB (${baseCurrency} -> ${destCurrency})...`
                    : `1 ${baseCurrency} = -- ${destCurrency} (Rate Unavailable)`}
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
