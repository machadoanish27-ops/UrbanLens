import React, { useState, useMemo } from 'react';
import { useUrban } from '../context/UrbanContext';
import { useCityEducation } from '../hooks/useUrbanLens';
import type { InstitutionItem } from '../types/api';
import {
  BookOpen,
  Globe,
  Award,
  Sparkles,
  CheckCircle2,
  ShieldCheck,
  Heart,
  GraduationCap,
  Building2,
  MapPin,
  ExternalLink,
  Search,
  RotateCcw,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';
import { sanitizeExternalUrl, getDisplayDomain } from '../utils/url';

export const EducationPage: React.FC = () => {
  const { currentCity, activeCityId } = useUrban();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');

  // Query live canonical education data from backend keyed to activeCityId
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

  // Local search filter
  const filteredInstitutions = useMemo(() => {
    if (!searchTerm.trim()) return rawInstitutions;
    const term = searchTerm.toLowerCase();
    return rawInstitutions.filter((item) => {
      const nameMatch = item.name?.toLowerCase().includes(term);
      const typeMatch = item.type?.toLowerCase().includes(term);
      const cityMatch = item.city?.toLowerCase().includes(term);
      return nameMatch || typeMatch || cityMatch;
    });
  }, [rawInstitutions, searchTerm]);

  // Reset filters
  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedType('ALL');
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-cyan-400" />
            <span>LINGUISTIC & HIGHER EDUCATION ECOSYSTEM</span>
            <span>·</span>
            <DataTrustBadge status="VERIFIED" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Education & Lifestyle
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Accredited universities, research institutes, linguistic diversity matrix, and student living suitability for {currentCity.name}, {currentCity.country}.
          </p>
        </div>
      </div>

      {/* UNIVERSITIES & HIGHER EDUCATION SECTION */}
      <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-6">
        {/* Section Header */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#1E334A] pb-5">
          <div>
            <div className="flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base sm:text-lg font-bold font-mono text-white uppercase tracking-wider">
                UNIVERSITIES & HIGHER EDUCATION
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-cyan-950 text-cyan-300 border border-cyan-500/30 font-semibold">
                {totalCount} Indexed
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-1">
              Canonical registry of colleges, polytechnics, and research universities in {currentCity.name}.
            </p>
          </div>

          {/* Search Bar */}
          <div className="relative w-full lg:w-80">
            <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search institutions by name..."
              className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-400 outline-none transition-colors"
            />
          </div>
        </div>

        {/* Type Filter Pills */}
        {availableTypes.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mr-1">
              Filter:
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
              QUERYING CANONICAL EDUCATION DATA FOR {currentCity.name}...
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
        {!isEduLoading && !isEduError && filteredInstitutions.length === 0 && (
          <div className="py-12 text-center rounded-xl bg-[#07111F] border border-[#1E334A] space-y-3 p-6">
            <Building2 className="w-8 h-8 text-slate-400 mx-auto" />
            <div className="text-xs font-mono text-slate-300 font-bold uppercase">
              NO INSTITUTIONS MATCHING FILTER
            </div>
            <p className="text-xs text-slate-400 font-sans max-w-md mx-auto">
              No educational institutions found matching &quot;{searchTerm}&quot; in {currentCity.name}.
            </p>
            <button
              onClick={handleResetFilters}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-300 text-xs font-mono transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Filters</span>
            </button>
          </div>
        )}

        {/* Institutions Grid */}
        {!isEduLoading && !isEduError && filteredInstitutions.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredInstitutions.map((inst) => (
              <div
                key={inst.institution_id}
                className="group rounded-xl bg-[#07111F] hover:bg-[#081527] border border-[#1E334A] hover:border-cyan-500/50 p-4 transition-all duration-200 flex flex-col justify-between shadow-md"
              >
                <div className="space-y-3">
                  {/* Top row: Type tag + Trust Badge */}
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950/80 text-cyan-300 border border-cyan-500/30 font-semibold tracking-wider uppercase">
                      {inst.type || 'Higher Education'}
                    </span>
                    <DataTrustBadge status="VERIFIED" size="sm" />
                  </div>

                  {/* Institution Name */}
                  <div>
                    <h3 className="text-sm font-bold font-mono text-white group-hover:text-cyan-300 transition-colors leading-snug line-clamp-2">
                      {inst.name}
                    </h3>
                    <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 mt-1.5">
                      <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                      <span className="truncate">
                        {inst.city || currentCity.name}, {inst.country_iso2 || currentCity.countryCode}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Bottom row: Provenance + Official Website Link */}
                <div className="pt-3 mt-3 border-t border-[#1E334A]/60 flex items-center justify-between gap-2">
                  <span className="text-[10px] font-mono text-slate-400 truncate max-w-[120px]">
                    {inst.source || 'Canonical Registry'}
                  </span>

                  {(() => {
                    const safeUrl = sanitizeExternalUrl(inst.website);
                    const domain = getDisplayDomain(inst.website);
                    return safeUrl ? (
                      <a
                        href={safeUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 hover:border-cyan-400 text-cyan-300 text-[11px] font-mono font-medium transition-all"
                      >
                        <span className="truncate max-w-[110px]">{domain || 'Website'}</span>
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>
                    ) : (
                      <span className="text-[10px] font-mono text-slate-400 italic">
                        Canonical Registry
                      </span>
                    );
                  })()}
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

      {/* Grid: Languages (Left 6) + Student & Lifestyle (Right 6) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* OFFICIAL vs SPOKEN LANGUAGES */}
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-6">
          <div className="border-b border-[#1E334A] pb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                LANGUAGE INTELLIGENCE
              </h2>
            </div>
            <span className="text-[10px] font-mono text-slate-400">STATUTORY & DIALECT REGISTER</span>
          </div>

          {/* Official Languages */}
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-2">
            <div className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">
              OFFICIAL STATUTORY LANGUAGES
            </div>
            <ul className="space-y-1.5 text-xs font-mono text-white">
              {currentCity.officialLanguages && currentCity.officialLanguages.length > 0 ? (
                currentCity.officialLanguages.map((lang: any, idx: number) => (
                  <li key={idx} className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{lang}</span>
                  </li>
                ))
              ) : (
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Official National Language of {currentCity.country}</span>
                </li>
              )}
            </ul>
            <div className="text-[10px] text-slate-400 font-mono pt-1">
              Source: {currentCity.name} Administrative Registry & National Census
            </div>
          </div>

          {/* Spoken Languages Survey */}
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-3">
            <div className="text-[10px] font-mono text-purple-300 font-bold uppercase tracking-wider">
              SPOKEN MUNICIPAL DIALECT DISTRIBUTION
            </div>
            <div className="space-y-2.5">
              {currentCity.spokenLanguages && currentCity.spokenLanguages.length > 0 ? (
                currentCity.spokenLanguages.map((item: any, idx: number) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-200">{item.name}</span>
                      <span className="text-purple-300 font-bold">{item.percentage}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-xs font-mono text-slate-400">
                  Dialect distribution survey currently syncing for {currentCity.name}.
                </div>
              )}
            </div>
            <div className="text-[10px] text-slate-400 font-mono pt-1">
              Source: Metropolitan Linguistic Census Survey ({currentCity.name})
            </div>
          </div>
        </div>

        {/* Student Suitability & Lifestyle Intelligence */}
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-6">
          <div className="border-b border-[#1E334A] pb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Heart className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                STUDENT SUITABILITY & LIFESTYLE
              </h2>
            </div>
            <DataTrustBadge status="INFERENCE" size="sm" />
          </div>

          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-start gap-3">
              <Award className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-xs font-bold font-mono text-white uppercase">
                  ACADEMIC CONNECTIVITY & MOBILITY
                </h3>
                <p className="text-xs text-slate-300 font-sans mt-1 leading-relaxed">
                  Metropolitan public transit networks and student concession corridors provide high mobility across {currentCity.name} academic hubs, libraries, and student residential quarters.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-xs font-bold font-mono text-white uppercase">
                  RESEARCH & ENTERPRISE COLLABORATION
                </h3>
                <p className="text-xs text-slate-300 font-sans mt-1 leading-relaxed">
                  Direct proximity between higher education institutions and regional commercial centers facilitates research translation, student employment, and technology incubator growth in {currentCity.name}.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-xs font-bold font-mono text-white uppercase">
                  URBAN SAFETY & CIVIC ENVIRONMENT
                </h3>
                <p className="text-xs text-slate-300 font-sans mt-1 leading-relaxed">
                  Monitored urban security, lighted transit connectors, and active civic infrastructure provide a reliable environment for students and relocating professionals in {currentCity.name}.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
