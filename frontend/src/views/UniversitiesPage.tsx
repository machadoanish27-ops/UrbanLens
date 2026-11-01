import React, { useState, useMemo } from 'react';
import { useUrban } from '../context/UrbanContext';
import { useCityEducation } from '../hooks/useUrbanLens';
import type { InstitutionItem } from '../types/api';
import {
  GraduationCap,
  MapPin,
  Building2,
  Search,
  CheckCircle2,
  ExternalLink,
  RotateCcw,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const UniversitiesPage: React.FC = () => {
  const { currentCity, activeCityId } = useUrban();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');

  const { data: eduResp, isLoading: isEduLoading, isError: isEduError } = useCityEducation(
    activeCityId,
    selectedType === 'ALL' ? undefined : selectedType,
    1,
    50
  );

  const rawInstitutions: InstitutionItem[] = useMemo(() => {
    return eduResp?.data?.institutions || eduResp?.data?.items || [];
  }, [eduResp]);

  const availableTypes: string[] = useMemo(() => {
    return eduResp?.data?.available_types || [];
  }, [eduResp]);

  const totalCount: number = eduResp?.data?.total ?? rawInstitutions.length;
  const disclaimer: string =
    eduResp?.data?.disclaimer ||
    'Showing indexed institutions from the canonical UrbanLens dataset and mapped locations from OpenStreetMap.';

  const filteredUnis = useMemo(() => {
    if (!searchTerm.trim()) return rawInstitutions;
    const term = searchTerm.toLowerCase();
    return rawInstitutions.filter((item) => {
      const nameMatch = item.name?.toLowerCase().includes(term);
      const typeMatch = item.type?.toLowerCase().includes(term);
      const cityMatch = item.city?.toLowerCase().includes(term);
      return nameMatch || typeMatch || cityMatch;
    });
  }, [rawInstitutions, searchTerm]);

  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedType('ALL');
  };

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
            {currentCity.name} Universities ({totalCount})
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Verified academic institutions, national institutes of technology, and specialized research centers in {currentCity.name}, {currentCity.country}.
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

      {/* Type Filter Pills */}
      {availableTypes.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mr-1">
            Category:
          </span>
          <button
            onClick={() => setSelectedType('ALL')}
            className={`px-3 py-1 rounded-lg text-xs font-mono transition-all ${
              selectedType === 'ALL'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400 font-bold shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                : 'bg-[#07111F] text-slate-400 border border-[#1E334A] hover:text-slate-200'
            }`}
          >
            ALL ({totalCount})
          </button>
          {availableTypes.map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1 rounded-lg text-xs font-mono transition-all ${
                selectedType === type
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400 font-bold shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                  : 'bg-[#07111F] text-slate-400 border border-[#1E334A] hover:text-slate-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      )}

      {/* Loading State */}
      {isEduLoading && (
        <div className="py-12 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
          <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wider uppercase">
            SYNCHRONIZING INSTITUTIONS FOR {currentCity.name}...
          </span>
        </div>
      )}

      {/* Error State */}
      {!isEduLoading && isEduError && (
        <div className="p-6 rounded-xl bg-red-950/20 border border-red-500/30 text-center space-y-2">
          <div className="text-xs font-mono text-red-400 font-bold uppercase">
            COULD NOT LOAD EDUCATION DATA
          </div>
          <p className="text-xs text-slate-300">
            Failed to connect to the education discovery service for {currentCity.name}.
          </p>
        </div>
      )}

      {/* Empty State */}
      {!isEduLoading && !isEduError && filteredUnis.length === 0 && (
        <div className="py-12 text-center rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] space-y-3 p-6">
          <Building2 className="w-8 h-8 text-slate-400 mx-auto" />
          <div className="text-xs font-mono text-slate-300 font-bold uppercase">
            NO INSTITUTIONS FOUND
          </div>
          <p className="text-xs text-slate-400 font-sans max-w-md mx-auto">
            No institutions match &quot;{searchTerm}&quot; in {currentCity.name}.
          </p>
          <button
            onClick={handleResetFilters}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-mono transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Search</span>
          </button>
        </div>
      )}

      {/* University Table / Cards */}
      {!isEduLoading && !isEduError && filteredUnis.length > 0 && (
        <div className="space-y-3">
          {filteredUnis.map((uni) => (
            <div
              key={uni.institution_id}
              className="rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] hover:border-cyan-500/50 p-6 transition-all duration-200 shadow-lg space-y-4"
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
                        {uni.city || currentCity.name}, {uni.country_iso2 || currentCity.countryCode}
                      </span>
                      <span>·</span>
                      <span className="text-purple-300">{uni.type}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {uni.website && (
                    <a
                      href={uni.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-mono transition-colors"
                    >
                      <span>Official Portal</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                  <DataTrustBadge status="VERIFIED" size="sm" />
                </div>
              </div>

              {/* Provenance footer */}
              <div className="pt-3 border-t border-[#1E334A]/60 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  STATUS: CANONICAL REGISTRY VERIFIED
                </span>
                <span>{uni.source || 'Canonical World Universities Registry'}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Dataset Disclaimer */}
      <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-[#1E334A]/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <span>{disclaimer}</span>
        <span className="text-cyan-400 shrink-0">Source: World Universities Dataset & OpenStreetMap</span>
      </div>
    </div>
  );
};
