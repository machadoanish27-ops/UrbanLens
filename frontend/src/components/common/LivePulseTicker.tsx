import React from 'react';
import { Link } from 'react-router-dom';
import { useUrban } from '../../context/UrbanContext';
import { useCityWeather, useCityAirQualityLive, useCurrencyConversion } from '../../hooks/useUrbanLens';
import { DataTrustBadge } from './DataTrustBadge';
import { Radio, ArrowUpRight } from 'lucide-react';

export const LivePulseTicker: React.FC = () => {
  const { activeCityId, currentCity } = useUrban();

  const { data: weatherResp } = useCityWeather(activeCityId);
  const { data: aqiResp } = useCityAirQualityLive(activeCityId);
  const { data: fxInr } = useCurrencyConversion('USD', 'INR', 1);
  const { data: fxJpy } = useCurrencyConversion('USD', 'JPY', 1);
  const { data: fxEur } = useCurrencyConversion('USD', 'EUR', 1);

  const cityName = currentCity?.name || weatherResp?.data?.city_name || 'Active City';
  const temp = weatherResp?.data?.weather?.current?.temperature_c ?? currentCity?.temperature;
  const rawPm25 = aqiResp?.data?.air_quality?.pollutants?.pm25;
  const aqiVal = typeof rawPm25 === 'number'
    ? Math.round(rawPm25)
    : (typeof currentCity?.aqi === 'number' ? currentCity.aqi : null);

  const streams = [
    {
      id: 'weather-pulse',
      category: 'WEATHER',
      name: `${cityName} Temp`,
      currentValue: temp !== undefined && temp !== null ? `${Math.round(temp)}°C` : 'Live Syncing',
      delta: weatherResp?.data?.weather?.current?.condition || 'Open-Meteo',
      trend: 'up' as const,
      status: 'OPTIMAL' as const,
      source: 'Open-Meteo Live API',
      trust: temp !== undefined && temp !== null ? 'LIVE' : 'CACHED',
      link: '/app/weather',
    },
    {
      id: 'aqi-pulse',
      category: 'AIR QUALITY',
      name: `${cityName} AQI`,
      currentValue: aqiVal !== null ? `AQI ${aqiVal}` : 'Syncing',
      delta: aqiVal !== null ? (aqiVal <= 50 ? 'Good' : aqiVal <= 100 ? 'Moderate' : 'Elevated') : 'Data Pending',
      trend: aqiVal !== null && aqiVal <= 50 ? ('up' as const) : ('down' as const),
      status: aqiVal !== null && aqiVal <= 50 ? ('OPTIMAL' as const) : ('MODERATE' as const),
      source: aqiResp?.data?.meta?.source || 'WHO / GlobalWeather',
      trust: aqiVal !== null ? 'LIVE' : 'DATA UNAVAILABLE',
      link: '/app/air-quality',
    },
    {
      id: 'fx-inr',
      category: 'CURRENCY',
      name: 'USD → INR',
      currentValue: fxInr?.data?.rate ? `₹${fxInr.data.rate.toFixed(2)}` : 'Syncing',
      delta: fxInr?.data?.status || 'Frankfurter ECB',
      trend: 'up' as const,
      status: 'OPTIMAL' as const,
      source: 'European Central Bank / Frankfurter',
      trust: 'LIVE',
      link: '/app/currency',
    },
    {
      id: 'fx-jpy',
      category: 'CURRENCY',
      name: 'USD → JPY',
      currentValue: fxJpy?.data?.rate ? `¥${fxJpy.data.rate.toFixed(2)}` : 'Syncing',
      delta: fxJpy?.data?.status || 'Frankfurter ECB',
      trend: 'up' as const,
      status: 'OPTIMAL' as const,
      source: 'European Central Bank / Frankfurter',
      trust: 'LIVE',
      link: '/app/currency',
    },
    {
      id: 'fx-eur',
      category: 'CURRENCY',
      name: 'USD → EUR',
      currentValue: fxEur?.data?.rate ? `€${fxEur.data.rate.toFixed(4)}` : 'Syncing',
      delta: fxEur?.data?.status || 'Frankfurter ECB',
      trend: 'up' as const,
      status: 'OPTIMAL' as const,
      source: 'European Central Bank / Frankfurter',
      trust: 'LIVE',
      link: '/app/currency',
    },
  ];

  return (
    <div className="w-full bg-[#07111F] border-b border-[#1E334A] py-2 px-4 lg:px-6 overflow-hidden">
      <div className="flex items-center gap-4 text-xs font-mono">
        <div className="flex items-center gap-1.5 text-cyan-400 font-bold shrink-0">
          <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span className="hidden sm:inline">GLOBAL TELEMETRY</span>
          <span className="text-slate-400">·</span>
        </div>

        <div className="flex items-center gap-6 overflow-x-auto no-scrollbar scroll-smooth">
          {streams.map((stream) => (
            <Link
              key={stream.id}
              to={stream.link}
              className="flex items-center gap-2 hover:bg-[#0B1726] px-2 py-1 rounded-lg transition-colors shrink-0 group"
            >
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">
                {stream.name}:
              </span>
              <span className="font-bold text-white group-hover:text-cyan-300 transition-colors">
                {stream.currentValue}
              </span>
              <span
                className={`text-[10px] px-1.5 py-0.2 rounded font-semibold ${
                  stream.status === 'OPTIMAL'
                    ? 'text-emerald-400 bg-emerald-950/40 border border-emerald-500/30'
                    : 'text-amber-400 bg-amber-950/40 border border-amber-500/30'
                }`}
              >
                {stream.delta}
              </span>
              <DataTrustBadge status={stream.trust as any} size="sm" />
              <ArrowUpRight className="w-3 h-3 text-slate-400 group-hover:text-cyan-400 transition-colors" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
