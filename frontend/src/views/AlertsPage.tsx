import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { AlertTriangle, MapPin, ArrowRight } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const { alerts, dismissAlert, setSelectedZone, currentCity, navigate } = useUrban();
  const [filterSeverity, setFilterSeverity] = useState<'ALL' | 'CRITICAL' | 'WARNING' | 'INFORMATIONAL'>('ALL');

  const filteredAlerts = filterSeverity === 'ALL'
    ? alerts
    : alerts.filter((a: any) => a.severity === filterSeverity);

  const handleOpenMap = (zoneId?: string) => {
    if (zoneId) {
      const z = currentCity.zones.find((zn: any) => zn.id === zoneId);
      if (z) setSelectedZone(z);
    }
    navigate('spatial');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-amber-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>INCIDENT DISPATCH & ANOMALIES</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Urban Alerts ({alerts.length})
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Real-time critical bottleneck warnings, environmental particulate threshold exceedances, and automated mitigation suggestions.
          </p>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#07111F] border border-[#1E334A]">
          {(['ALL', 'CRITICAL', 'WARNING', 'INFORMATIONAL'] as const).map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-3 py-1.5 text-xs font-mono rounded-lg transition-colors ${
                filterSeverity === sev
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="p-12 text-center rounded-2xl bg-[#0B1726] border border-[#1E334A] text-slate-400 font-mono text-xs">
            No active alerts matching filter "{filterSeverity}".
          </div>
        ) : (
          filteredAlerts.map((alert: any) => {
            const isCrit = alert.severity === 'CRITICAL';
            const isWarn = alert.severity === 'WARNING';

            return (
              <div
                key={alert.id}
                className="rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/50 p-6 transition-all duration-200 shadow-xl space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold ${
                        isCrit
                          ? 'bg-rose-950 text-rose-400 border border-rose-500/40'
                          : isWarn
                          ? 'bg-amber-950 text-amber-400 border border-amber-500/40'
                          : 'bg-blue-950 text-blue-400 border border-blue-500/40'
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <h3 className="text-base font-bold font-mono text-white">
                      {alert.title}
                    </h3>
                  </div>

                  <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                    <span>{alert.time}</span>
                    <span>·</span>
                    <span className="text-purple-300">{alert.confidence}% CONF</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-1">
                    <div className="text-[10px] font-mono text-slate-400 uppercase">LOCATION & SIGNAL</div>
                    <div className="text-cyan-300 font-mono font-semibold flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5" />
                      {alert.location}
                    </div>
                    <p className="text-slate-300 font-sans mt-1">
                      {alert.signal}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-1">
                    <div className="text-[10px] font-mono text-cyan-300 uppercase font-bold">
                      RECOMMENDED MITIGATION
                    </div>
                    <p className="text-slate-200 font-sans leading-relaxed">
                      {alert.recommendedAction}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-2 border-t border-[#1E334A] text-xs font-mono">
                  <button
                    onClick={() => handleOpenMap(alert.zoneId)}
                    className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1.5"
                  >
                    <span>LOCATE ON SPATIAL MAP</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => navigate('optimization')}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold"
                    >
                      RUN PSO MITIGATION
                    </button>
                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="px-3 py-1.5 rounded-lg bg-[#07111F] border border-[#1E334A] text-slate-400 hover:text-white"
                    >
                      DISMISS
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
