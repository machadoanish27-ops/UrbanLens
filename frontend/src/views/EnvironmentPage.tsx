import React from 'react';
import { useUrban } from '../context/UrbanContext';
import { useCityWeather, useCityAirQualityLive } from '../hooks/useUrbanLens';
import {
  CloudSun,
  Wind,
  Thermometer,
  Droplets,
  Activity,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const EnvironmentPage: React.FC = () => {
  const { currentCity, activeCityId } = useUrban();

  const { data: weatherResp, isLoading: isWeatherLoading } = useCityWeather(activeCityId);
  const { data: aqiResp, isLoading: isAqiLoading } = useCityAirQualityLive(activeCityId);

  const weather = weatherResp?.data?.weather?.current;
  const aqiData = aqiResp?.data?.air_quality;

  const temp = typeof weather?.temperature_c === 'number'
    ? Math.round(weather.temperature_c)
    : currentCity.temperature;
  const feelsLike = typeof weather?.apparent_temperature_c === 'number'
    ? Math.round(weather.apparent_temperature_c)
    : currentCity.feelsLike;
  const humidity = typeof weather?.relative_humidity_pct === 'number'
    ? Math.round(weather.relative_humidity_pct)
    : currentCity.humidity;
  const wind = typeof weather?.wind_speed_kph === 'number'
    ? `${weather.wind_speed_kph} km/h`
    : currentCity.windSpeed;

  const pm25 = typeof aqiData?.pollutants?.pm25 === 'number'
    ? aqiData.pollutants.pm25
    : currentCity.pm25;
  const pm10 = typeof aqiData?.pollutants?.pm10 === 'number'
    ? aqiData.pollutants.pm10
    : currentCity.pm10;
  const no2 = typeof aqiData?.pollutants?.no2 === 'number'
    ? aqiData.pollutants.no2
    : currentCity.no2;
  const o3 = typeof aqiData?.pollutants?.o3 === 'number'
    ? aqiData.pollutants.o3
    : currentCity.o3;

  const rawAqi = pm25 !== null && pm25 !== undefined ? Math.round(pm25) : currentCity.aqi;
  const aqiCategory = rawAqi !== null
    ? (rawAqi <= 50 ? 'Good' : rawAqi <= 100 ? 'Moderate' : rawAqi <= 150 ? 'Unhealthy for Sensitive' : rawAqi <= 200 ? 'Unhealthy' : 'Very Unhealthy')
    : 'DATA UNAVAILABLE';

  const weatherSource = weatherResp?.data?.meta?.source || 'Open-Meteo Surface Reanalysis';
  const aqiSource = aqiResp?.data?.meta?.source || 'WHO / Global Air Quality Network';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <CloudSun className="w-4 h-4 text-cyan-400" />
            <span>METEOROLOGICAL & AIR SPECTROMETRY</span>
            <span>·</span>
            <DataTrustBadge status={isWeatherLoading || isAqiLoading ? 'INFERENCE' : 'LIVE'} size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Environmental Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Live telemetry monitoring surface particulates, meteorological soundings, ground ozone, and atmospheric dynamics.
          </p>
        </div>

        <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-right">
          <div className="text-[10px] font-mono text-slate-400">PROVENANCE SOURCE</div>
          <div className="text-xs font-bold font-mono text-cyan-400 truncate max-w-xs">{weatherSource}</div>
          <div className="text-[10px] font-mono text-slate-400 mt-1">{aqiSource}</div>
        </div>
      </div>

      {/* Surface Weather Parameters */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Thermometer className="w-4 h-4 text-amber-400" />
            <span>TEMPERATURE</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-white mt-1">
            {temp !== null && temp !== undefined ? `${temp}°C` : 'DATA UNAVAILABLE'}
          </div>
          <div className="text-xs text-slate-400 font-mono mt-1">
            {feelsLike !== null && feelsLike !== undefined ? `Feels like ${feelsLike}°C` : 'Real-time observation'}
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Droplets className="w-4 h-4 text-blue-400" />
            <span>HUMIDITY</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-white mt-1">
            {humidity !== null && humidity !== undefined ? `${humidity}%` : 'DATA UNAVAILABLE'}
          </div>
          <div className="text-xs text-blue-400 font-mono mt-1">
            {weatherResp?.data?.weather?.current?.condition || 'Surface hygrometer'}
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Wind className="w-4 h-4 text-cyan-400" />
            <span>SURFACE WIND</span>
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold font-mono text-white mt-1 truncate">
            {wind || 'DATA UNAVAILABLE'}
          </div>
          <div className="text-xs text-cyan-400 font-mono mt-1">
            Anemometer vector telemetry
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#0B1726] border border-[#1E334A]">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 mb-1">
            <Activity className="w-4 h-4 text-purple-400" />
            <span>AIR QUALITY INDEX</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-purple-400 mt-1">
            {rawAqi !== null && rawAqi !== undefined ? `AQI ${rawAqi}` : 'DATA UNAVAILABLE'}
          </div>
          <div className="text-xs text-slate-300 font-mono mt-1">
            {aqiCategory}
          </div>
        </div>
      </div>

      {/* Atmospheric Gas Composition Array */}
      <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
          <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
            PARTICULATE & GAS SPECTROMETRY TELEMETRY
          </h2>
          <span className="text-[10px] font-mono text-slate-400">EPA & WHO STANDARDS</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>FINE PARTICLES (PM2.5)</span>
              <span className="text-purple-400 font-bold">
                {pm25 !== null && pm25 !== undefined ? `${pm25} µg/m³` : 'DATA UNAVAILABLE'}
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-purple-500 rounded-full"
                style={{ width: `${Math.min(100, ((pm25 || 0) / 150) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Target &lt; 15 µg/m³</div>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>COARSE PARTICLES (PM10)</span>
              <span className="text-amber-400 font-bold">
                {pm10 !== null && pm10 !== undefined ? `${pm10} µg/m³` : 'DATA UNAVAILABLE'}
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-amber-500 rounded-full"
                style={{ width: `${Math.min(100, ((pm10 || 0) / 200) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Target &lt; 45 µg/m³</div>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>NITROGEN DIOXIDE (NO₂)</span>
              <span className="text-cyan-400 font-bold">
                {no2 !== null && no2 !== undefined ? `${no2} ppb` : 'DATA UNAVAILABLE'}
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-cyan-400 rounded-full"
                style={{ width: `${Math.min(100, ((no2 || 0) / 100) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Vehicular combustion indicator</div>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A]">
            <div className="flex justify-between text-xs font-mono text-slate-400">
              <span>GROUND OZONE (O₃)</span>
              <span className="text-emerald-400 font-bold">
                {o3 !== null && o3 !== undefined ? `${o3} ppb` : 'DATA UNAVAILABLE'}
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full mt-3 overflow-hidden">
              <div
                className="h-full bg-emerald-400 rounded-full"
                style={{ width: `${Math.min(100, ((o3 || 0) / 80) * 100)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 font-mono mt-2">Photochemical atmospheric indicator</div>
          </div>
        </div>
      </div>
    </div>
  );
};
