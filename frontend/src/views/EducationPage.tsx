import React from 'react';
import { useUrban } from '../context/UrbanContext.tsx';
import { BookOpen, Globe, Award, Sparkles, CheckCircle2, ShieldCheck, Heart } from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge.tsx';

export const EducationPage: React.FC = () => {
  const { currentCity } = useUrban();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-cyan-400" />
            <span>LINGUISTIC & STUDENT ECOSYSTEM</span>
            <span>·</span>
            <DataTrustBadge status="VERIFIED" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Education & Lifestyle
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Linguistic diversity matrix, student living suitability, and cultural infrastructure intelligence with explicit separation of state official vs spoken municipal dialects.
          </p>
        </div>
      </div>

      {/* Grid: Languages (Left 6) + Student & Lifestyle (Right 6) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Section 19: OFFICIAL vs SPOKEN LANGUAGES */}
        <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-6">
          <div className="border-b border-[#1E334A] pb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                LANGUAGE INTELLIGENCE
              </h2>
            </div>
            <span className="text-[10px] font-mono text-slate-400">STATE STATUTORY VS SURVEY</span>
          </div>

          {/* Official Languages */}
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-2">
            <div className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">
              OFFICIAL STATUTORY LANGUAGES
            </div>
            <ul className="space-y-1.5 text-xs font-mono text-white">
              {currentCity.officialLanguages.map((lang: any, idx: number) => (
                <li key={idx} className="flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{lang}</span>
                </li>
              ))}
            </ul>
            <div className="text-[10px] text-slate-400 font-mono pt-1">
              Source: Official Gazette of Maharashtra / Municipal Corporation Registry
            </div>
          </div>

          {/* Spoken Languages Survey */}
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-3">
            <div className="text-[10px] font-mono text-purple-300 font-bold uppercase tracking-wider">
              SPOKEN MUNICIPAL DIALECT DISTRIBUTION
            </div>
            <div className="space-y-2.5">
              {currentCity.spokenLanguages.map((item: any, idx: number) => (
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
              ))}
            </div>
            <div className="text-[10px] text-slate-400 font-mono pt-1">
              Source: Metropolitan Linguistic Census Survey (Urban Area Sampling)
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
                  ACADEMIC AFFORDABILITY & CONNECTIVITY
                </h3>
                <p className="text-xs text-slate-300 font-sans mt-1 leading-relaxed">
                  Suburban railway passes provide high mobility at minimal cost (₹315/month). Powai, Matunga, and Vile Parle form dense student clusters with accessible cafeterias and libraries.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-xs font-bold font-mono text-white uppercase">
                  RESEARCH & INDUSTRY PARTNERSHIPS
                </h3>
                <p className="text-xs text-slate-300 font-sans mt-1 leading-relaxed">
                  Direct proximity between engineering institutions (IIT Bombay, VJTI) and technology enterprise hubs (BKC, Powai, SEEPZ) facilitates high patent filing and research translation.
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-start gap-3">
              <ShieldCheck className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-xs font-bold font-mono text-white uppercase">
                  URBAN SAFETY INDEX
                </h3>
                <p className="text-xs text-slate-300 font-sans mt-1 leading-relaxed">
                  Ranked among India's safest metropolitan centers for night transit and solo student mobility, reinforced by 24/7 suburban train operations and CCTV surveillance.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
