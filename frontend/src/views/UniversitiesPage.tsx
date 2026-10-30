import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import {
  GraduationCap,
  MapPin,
  Building2,
  Search,
  CheckCircle2
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const UniversitiesPage: React.FC = () => {
  const { currentCity } = useUrban();
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredUniId, setHoveredUniId] = useState<string | null>(null);

  const filteredUnis = currentCity.universities.filter((u: any) =>
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.specialization.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-cyan-400" />
            <span>ACADEMIC & RESEARCH HUBS</span>
            <span>·</span>
            <DataTrustBadge status="VERIFIED" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Universities ({currentCity.universities.length})
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Verified academic institutions, national institutes of technology, and specialized research centers powering metropolitan talent pipelines.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search universities..."
            className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-400 outline-none"
          />
        </div>
      </div>

      {/* University Table / Cards (Section 18) */}
      <div className="space-y-3">
        {filteredUnis.map((uni: any) => {
          const isHovered = hoveredUniId === uni.id;

          return (
            <div
              key={uni.id}
              onMouseEnter={() => setHoveredUniId(uni.id)}
              onMouseLeave={() => setHoveredUniId(null)}
              className="rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] hover:border-cyan-500/50 p-6 transition-all duration-200 cursor-pointer shadow-lg space-y-4"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-cyan-400 shrink-0">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold font-mono text-white hover:text-cyan-300 transition-colors">
                      {uni.name}
                    </h3>
                    <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-slate-400 mt-1">
                      <span className="flex items-center gap-1 text-slate-300">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                        {uni.location}
                      </span>
                      <span>·</span>
                      <span className="text-purple-300">{uni.type}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded-lg text-xs font-mono bg-cyan-950 text-cyan-300 border border-cyan-500/30 font-semibold">
                    {uni.ranking}
                  </span>
                  <DataTrustBadge status="VERIFIED" size="sm" />
                </div>
              </div>

              {/* Grid Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 border-t border-[#1E334A]/60 text-xs font-mono">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase">STUDENTS & SCHOLARS</span>
                  <div className="text-white font-semibold mt-0.5">{uni.studentsCount}</div>
                </div>
                <div className="md:col-span-2">
                  <span className="text-[10px] text-slate-400 uppercase">RESEARCH SPECIALIZATION</span>
                  <div className="text-cyan-300 font-semibold mt-0.5 truncate">{uni.specialization}</div>
                </div>
              </div>

              {/* Hover Expansion with Additional Verified Information */}
              {isHovered && (
                <div className="pt-3 border-t border-[#1E334A] text-xs font-sans text-slate-300 flex items-center justify-between animate-in fade-in duration-150">
                  <span className="flex items-center gap-1.5 text-emerald-400 font-mono text-[11px]">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    STATUS: {uni.status}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    GOVERNMENT OF INDIA ACCREDITED HIGHER EDUCATION REGISTRY
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
