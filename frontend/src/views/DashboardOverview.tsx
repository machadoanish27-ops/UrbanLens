import React from 'react';
import { useUrban } from '../context/UrbanContext';
import { MetricCard } from '../components/common/MetricCard';
import { CityMapCanvas } from '../components/common/CityMapCanvas';
import {
  Users,
  Wind,
  Thermometer,
  Car,
  GraduationCap,
  Coins,
  Sparkles,
  AlertTriangle,
  ArrowRight,
  Cpu,
  Compass
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const DashboardOverview: React.FC = () => {
  const { currentCity, toggleAiModal, navigate, alerts, setSelectedZone } = useUrban();

  return (
    <div className="space-y-6">
      {/* Command Center Greeting & City Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 tracking-wider uppercase font-semibold flex items-center gap-2">
            <span>Good morning.</span>
            <span>·</span>
            <span className="text-emerald-400">● TELEMETRY SYNCHRONIZED</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Intelligence Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl leading-relaxed">
            Real-time urban intelligence across mobility, environment, infrastructure, and human activity.
          </p>
        </div>

        {/* Quick Command Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => navigate('spatial')}
            className="px-3.5 py-2 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-200 transition-colors flex items-center gap-1.5"
          >
            <Compass className="w-3.5 h-3.5 text-cyan-400" />
            <span>SPATIAL TWIN</span>
          </button>
          <button
            onClick={() => navigate('optimization')}
            className="px-3.5 py-2 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-emerald-500/40 text-xs font-mono text-slate-200 transition-colors flex items-center gap-1.5"
          >
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>PSO SWARM</span>
          </button>
          <button
            onClick={() => toggleAiModal(true)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-xs tracking-wider transition-all shadow-[0_0_15px_rgba(34,211,238,0.25)] flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>✦ ASK URBANLENS</span>
          </button>
        </div>
      </div>

      {/* 6 High-Fidelity Primary Metric Cards (Section 7) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* 1. Population */}
        <MetricCard
          title="Population"
          value={currentCity.population}
          unit="residents"
          change="+1.2%"
          trend="up"
          icon={Users}
          sparkline={[20.4, 20.7, 21.0, 21.1, 21.2, 21.3, 21.35]}
          source="Census & Telecom Micro-grid"
          updateTime="00:00 UTC"
          trust="VERIFIED"
          accentColor="blue"
          detailNote={`Density: ${currentCity.density}. High concentration in suburban transit nodes.`}
          onClick={() => navigate('analytics')}
        />

        {/* 2. Air Quality */}
        <MetricCard
          title="Air Quality"
          value={`AQI ${currentCity.aqi}`}
          unit={currentCity.aqiCategory}
          change="-4.2%"
          trend="down"
          icon={Wind}
          sparkline={[172, 168, 164, 160, 159, 158, 158]}
          source="Municipal Laser Gas Spectrometry"
          updateTime="14:30 UTC"
          trust="LIVE"
          accentColor={currentCity.aqi > 150 ? 'rose' : currentCity.aqi > 100 ? 'amber' : 'emerald'}
          detailNote={`PM2.5: ${currentCity.pm25} µg/m³ · PM10: ${currentCity.pm10} µg/m³. Coastal sea-breeze transition active.`}
          onClick={() => navigate('environment')}
        />

        {/* 3. Temperature */}
        <MetricCard
          title="Temperature"
          value={`${currentCity.temperature}°C`}
          unit={`Feels like ${currentCity.feelsLike}°C`}
          change="+0.5°"
          trend="up"
          icon={Thermometer}
          sparkline={[28, 29, 30, 31, 31, 31, 31]}
          source="Doppler Surface Weather Stations"
          updateTime="14:32 UTC"
          trust="LIVE"
          accentColor="amber"
          detailNote={`Humidity: ${currentCity.humidity}% · Wind: ${currentCity.windSpeed}. Urban heat island delta +2.8°C.`}
          onClick={() => navigate('environment')}
        />

        {/* 4. Traffic Flow */}
        <MetricCard
          title="Traffic Load"
          value={`${currentCity.trafficLoad}%`}
          unit="capacity index"
          change={currentCity.trafficTrend}
          trend={currentCity.trafficTrend.startsWith('+') ? 'up' : 'down'}
          icon={Car}
          sparkline={[58, 62, 64, 65, 66, 67, 68]}
          source="Computer Vision Transit Feeds"
          updateTime="14:32 UTC"
          trust="LIVE"
          accentColor="cyan"
          detailNote="Western Express Corridor & BKC connector experiencing high load approaching evening peak."
          onClick={() => navigate('spatial')}
        />

        {/* 5. Universities */}
        <MetricCard
          title="Higher Ed"
          value={`${currentCity.universities.length}`}
          unit="institutions"
          change="NIRF Top"
          trend="neutral"
          icon={GraduationCap}
          sparkline={[6, 6, 6, 6, 6, 6, 6]}
          source="Higher Education Accreditation Council"
          updateTime="Annual 2026"
          trust="VERIFIED"
          accentColor="violet"
          detailNote="Includes IIT Bombay, University of Mumbai, TIFR, VJTI, and ICT."
          onClick={() => navigate('universities')}
        />

        {/* 6. Cost of Living */}
        <MetricCard
          title="Cost Index"
          value={currentCity.costOfLivingIndex ? `${currentCity.costOfLivingIndex}` : 'UNAVAILABLE'}
          unit={currentCity.costOfLivingIndex ? 'Base NYC=100' : 'No Data'}
          change={currentCity.costOfLivingIndex ? '-0.8%' : 'N/A'}
          trend="neutral"
          icon={Coins}
          sparkline={currentCity.costOfLivingIndex ? [35.1, 34.8, 34.5, 34.4, 34.3, 34.2, 34.2] : [0, 0, 0, 0, 0, 0, 0]}
          source="Global Numbeo & Municipal Index"
          updateTime="Q3 2026"
          trust={currentCity.costOfLivingIndex ? 'VERIFIED' : 'DATA UNAVAILABLE'}
          accentColor={currentCity.costOfLivingIndex ? 'emerald' : 'rose'}
          detailNote={currentCity.costOfLivingIndex ? 'Housing index 24.8. Rent-to-income ratio optimal for technical talent.' : 'UrbanLens does not currently have verified city-level cost data.'}
          onClick={() => navigate('cost-of-living')}
        />
      </div>

      {/* Main Map Visual Canvas & Intelligence Inspector */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold font-mono uppercase text-white tracking-wider">
              SPATIAL CORRIDORS & ANOMALY SURVEILLANCE
            </h2>
            <DataTrustBadge status="LIVE" size="sm" />
          </div>
          <button
            onClick={() => navigate('spatial')}
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <span>FULL OPERATIONAL SPATIAL DESK</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <CityMapCanvas heightClass="h-[520px]" />
      </div>

      {/* Bottom Section: Active Anomalies & Multi-Zone Pulse */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Active Telemetry Alerts */}
        <div className="lg:col-span-2 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                ACTIVE URBAN TELEMETRY ALERTS ({alerts.length})
              </h3>
            </div>
            <button
              onClick={() => navigate('alerts')}
              className="text-xs font-mono text-cyan-400 hover:underline"
            >
              VIEW ALL ALERTS →
            </button>
          </div>

          <div className="space-y-3">
            {alerts.slice(0, 3).map((alert: any) => (
              <div
                key={alert.id}
                onClick={() => {
                  if (alert.zoneId) {
                    const z = currentCity.zones.find((zn: any) => zn.id === alert.zoneId);
                    if (z) setSelectedZone(z);
                  }
                  navigate('alerts');
                }}
                className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 transition-colors cursor-pointer group"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        alert.severity === 'CRITICAL'
                          ? 'bg-rose-950 text-rose-400 border border-rose-500/40'
                          : 'bg-amber-950 text-amber-400 border border-amber-500/40'
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs font-bold text-white font-mono group-hover:text-cyan-300 transition-colors">
                      {alert.title}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">{alert.time}</span>
                </div>

                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {alert.signal}
                </p>

                <div className="mt-2.5 pt-2 border-t border-[#1E334A]/60 flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-400 truncate max-w-[280px]">Location: {alert.location}</span>
                  <span className="text-cyan-400 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                    Mitigate <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Quick AI Insight Card */}
        <div className="rounded-2xl bg-gradient-to-b from-[#0B1726] to-[#07111F] border border-cyan-500/30 p-5 space-y-4 flex flex-col justify-between shadow-[0_0_25px_rgba(34,211,238,0.08)]">
          <div>
            <div className="flex items-center justify-between border-b border-[#1E334A] pb-3 mb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold font-mono text-white uppercase tracking-wider">
                  AI CAUSAL SYNTHESIS
                </h3>
              </div>
              <DataTrustBadge status="INFERENCE" size="sm" />
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-[10px] font-mono text-slate-400 font-bold uppercase">CORRIDOR ANOMALY</span>
                <p className="text-white font-medium mt-0.5">
                  Bandra West and Western Express Highway converging at 72% flow saturation.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-purple-950/20 border border-purple-500/30">
                <span className="text-[10px] font-mono text-purple-300 font-bold uppercase">PREDICTIVE IMPACT</span>
                <p className="text-slate-200 mt-1">
                  Queue length expected to hit 2.1 km by 18:00 unless signal cycle duration is modified.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-4 border-t border-[#1E334A]">
            <button
              onClick={() => toggleAiModal(true)}
              className="w-full py-2.5 rounded-xl bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-500/40 text-cyan-300 text-xs font-mono font-semibold transition-colors flex items-center justify-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>ENGAGE REASONING ASSISTANT</span>
            </button>
            <button
              onClick={() => navigate('optimization')}
              className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold transition-all shadow-md flex items-center justify-center gap-2"
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>RUN SWARM SIGNAL OPTIMIZER</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
