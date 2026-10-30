import React from 'react';
import { useUrban } from '../context/UrbanContext';
import { MapPin, LogOut } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const ProfilePage: React.FC = () => {
  const { user, currentCity, logoutUser, navigate, setCityById } = useUrban();

  const savedCities = ['mumbai', 'tokyo', 'london'];

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="p-8 rounded-2xl bg-[#0B1726] border border-[#1E334A] flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-5">
          <div className="relative">
            <img
              src={user.avatarUrl}
              alt={user.name}
              className="w-20 h-20 rounded-2xl border-2 border-cyan-500/50 object-cover shadow-[0_0_20px_rgba(34,211,238,0.2)]"
            />
            <span className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 border-2 border-[#0B1726] flex items-center justify-center text-[9px] font-bold text-slate-950">
              ✓
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black font-mono text-white uppercase">
                {user.name}
              </h1>
              <DataTrustBadge status="VERIFIED" size="sm" />
            </div>
            <p className="text-xs font-mono text-cyan-400 mt-0.5">{user.role}</p>
            <p className="text-xs text-slate-400 font-mono mt-0.5">{user.organization}</p>
          </div>
        </div>

        <button
          onClick={logoutUser}
          className="px-4 py-2.5 rounded-xl bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/40 text-rose-300 text-xs font-mono font-bold transition-colors flex items-center gap-2 self-start md:self-auto"
        >
          <LogOut className="w-4 h-4" />
          <span>SIGN OUT</span>
        </button>
      </div>

      {/* Profile Grid: Active Assignment & Saved Cities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Grid Assignment */}
        <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-cyan-400" />
              <h2 className="text-xs font-bold font-mono text-white uppercase tracking-wider">
                CURRENT COMMAND GRID
              </h2>
            </div>
            <span className="text-xs font-mono text-emerald-400 font-bold">● ACTIVE</span>
          </div>

          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-2">
            <h3 className="text-lg font-bold font-mono text-white uppercase">{currentCity.name} · {currentCity.country}</h3>
            <p className="text-xs text-slate-400 font-mono">Coordinates: {currentCity.coordinates}</p>
            <div className="pt-2 flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">Current AQI: <strong className="text-purple-400">{currentCity.aqi}</strong></span>
              <span className="text-slate-400">Traffic Load: <strong className="text-amber-400">{currentCity.trafficLoad}%</strong></span>
            </div>
          </div>
        </div>

        {/* Saved Cities */}
        <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-4">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
            <h2 className="text-xs font-bold font-mono text-white uppercase tracking-wider">
              SAVED METROPOLITAN NODES
            </h2>
            <button onClick={() => navigate('cities')} className="text-xs font-mono text-cyan-400 hover:underline">
              Browse All →
            </button>
          </div>

          <div className="space-y-2">
            {savedCities.map((cId) => (
              <button
                key={cId}
                onClick={() => {
                  setCityById(cId);
                  navigate('dashboard');
                }}
                className="w-full p-3 rounded-xl bg-[#07111F] hover:bg-cyan-950/40 border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-white flex items-center justify-between transition-colors"
              >
                <span className="uppercase font-bold">{cId}</span>
                <span className="text-cyan-400">SWITCH GRID →</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
