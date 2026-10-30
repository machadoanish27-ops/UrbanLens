import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUrban } from '../context/UrbanContext';
import {
  ArrowRight,
  Sparkles,
  Compass,
  Globe2,
  BookOpen,
  DollarSign
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const LandingPage: React.FC = () => {
  const { setActiveCityId } = useUrban();
  const navigate = useNavigate();

  const featuredCities = [
    { id: 'city_1392685764', name: 'Tokyo', country: 'Japan', iso: 'JP', pop: '37,435,191', tag: 'High-Tech Mega-Hub' },
    { id: 'city_1826645935', name: 'London', country: 'United Kingdom', iso: 'GB', pop: '9,002,488', tag: 'Global Financial Center' },
    { id: 'city_1356226629', name: 'Mumbai', country: 'India', iso: 'IN', pop: '21,357,000', tag: 'Commercial Capital' },
    { id: 'city_1840034016', name: 'New York', country: 'United States', iso: 'US', pop: '8,804,190', tag: 'Metropolitan Benchmark' },
  ];

  const handleLaunchCity = (cityId: string) => {
    setActiveCityId(cityId);
    navigate(`/app/city/${cityId}`);
  };

  return (
    <div className="min-h-screen bg-[#030712] text-[#F8FAFC] selection:bg-cyan-500/20 selection:text-cyan-300 font-sans">
      {/* Top Public Navigation */}
      <header className="sticky top-0 z-50 w-full h-20 bg-[#030712]/90 backdrop-blur-md border-b border-[#1E334A] px-6 lg:px-12 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 p-[1px] shadow-[0_0_20px_rgba(34,211,238,0.3)]">
            <div className="w-full h-full bg-[#030712] rounded-xl flex items-center justify-center">
              <span className="font-mono font-extrabold text-cyan-400 text-sm">UL</span>
            </div>
          </div>
          <div>
            <div className="text-lg font-black tracking-widest font-display text-white">
              URBANLENS
            </div>
            <div className="text-[10px] font-mono tracking-widest text-slate-400">
              GLOBAL CITY INTELLIGENCE PLATFORM
            </div>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-mono text-slate-300 tracking-wider">
          <a href="#capabilities" className="hover:text-cyan-400 transition-colors">CAPABILITIES</a>
          <a href="#cities" className="hover:text-cyan-400 transition-colors">FEATURED CITIES</a>
          <a href="#architecture" className="hover:text-cyan-400 transition-colors">PROVENANCE & RAG</a>
          <Link to="/app/ask" className="hover:text-cyan-400 transition-colors">ASK AI</Link>
          <Link to="/app/compare" className="hover:text-cyan-400 transition-colors">COMPARE</Link>
        </nav>

        {/* Action CTAs */}
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="px-4 py-2 text-xs font-mono font-semibold text-slate-300 hover:text-white transition-colors"
          >
            SIGN IN
          </Link>
          <Link
            to="/app"
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-mono font-bold tracking-wider shadow-[0_0_20px_rgba(34,211,238,0.3)] hover:shadow-[0_0_30px_rgba(34,211,238,0.5)] transition-all flex items-center gap-1.5"
          >
            <span>ENTER PLATFORM</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative min-h-[85vh] flex items-center justify-center px-6 lg:px-12 py-16 overflow-hidden">
        {/* Background Digital City Graphic */}
        <div className="absolute inset-0 z-0">
          <img
            src="/src/assets/images/hero_digital_city_1793341279762.jpg"
            alt="Futuristic Digital City"
            className="w-full h-full object-cover opacity-25 filter brightness-70 scale-105"
            onError={(e) => {
              (e.currentTarget as HTMLElement).style.display = 'none';
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/75 to-[#030712]/30" />
          <div className="absolute inset-0 bg-spatial-grid opacity-30" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#0B1726]/80 border border-cyan-500/40 backdrop-blur-md text-xs font-mono text-cyan-300 shadow-[0_0_15px_rgba(34,211,238,0.15)]">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>GLOBAL AI URBAN INTELLIGENCE OPERATING SYSTEM</span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-black font-display tracking-tight text-white leading-tight uppercase">
            UNDERSTAND ANY CITY. <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              CHOOSE WHERE YOU BELONG.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-sm sm:text-base text-slate-300 font-sans leading-relaxed">
            A source-grounded global relocation and urban telemetry platform powered by canonical city data, 7 domain intelligence agents, authoritative RAG knowledge, and live provider observations.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/app/explore"
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-xs sm:text-sm tracking-wider shadow-[0_0_30px_rgba(34,211,238,0.4)] transition-all flex items-center justify-center gap-2"
            >
              <Compass className="w-4 h-4" />
              <span>EXPLORE 50,000+ CITIES</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/app/ask"
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-[#0B1726]/90 hover:bg-[#1E334A] border border-[#1E334A] hover:border-cyan-500/40 text-white font-mono font-semibold text-xs sm:text-sm tracking-wider transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>ASK AI INTELLIGENCE</span>
            </Link>
          </div>

          {/* Verified Stats Row */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto pt-10">
            <div className="p-4 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] text-center">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-cyan-400">50,250</div>
              <div className="text-[11px] font-mono text-slate-400 uppercase mt-0.5">CANONICAL CITIES</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] text-center">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-emerald-400">215</div>
              <div className="text-[11px] font-mono text-slate-400 uppercase mt-0.5">COUNTRIES COVERED</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] text-center">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-purple-400">9,350</div>
              <div className="text-[11px] font-mono text-slate-400 uppercase mt-0.5">VERIFIED UNIVERSITIES</div>
            </div>
            <div className="p-4 rounded-2xl bg-[#0B1726]/80 border border-[#1E334A] text-center">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-amber-400">35 DOCS</div>
              <div className="text-[11px] font-mono text-slate-400 uppercase mt-0.5">AUTHORITATIVE RAG CORPUS</div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Cities Section */}
      <section id="cities" className="py-20 px-6 lg:px-12 border-t border-[#1E334A] bg-[#07111F]/50">
        <div className="max-w-6xl mx-auto space-y-10">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-2 text-xs font-mono text-cyan-400 tracking-widest font-semibold uppercase">
              <Globe2 className="w-4 h-4" />
              <span>GLOBAL NODES</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-black font-display uppercase tracking-tight text-white">
              Launch Metropolitan Intelligence
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 font-sans">
              Inspect real-time telemetry, live Open-Meteo climate, WHO air quality, and Numbeo-calibrated cost of living across representative metropolitan hubs.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {featuredCities.map((city) => (
              <div
                key={city.id}
                onClick={() => handleLaunchCity(city.id)}
                className="group relative p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/50 hover:shadow-[0_0_25px_rgba(34,211,238,0.15)] transition-all cursor-pointer flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xl font-bold font-mono text-white group-hover:text-cyan-300 transition-colors">
                      {city.name}
                    </span>
                    <DataTrustBadge status="LIVE" size="sm" />
                  </div>
                  <div className="text-xs font-mono text-slate-400">{city.country} ({city.iso})</div>
                  <div className="mt-4 p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs font-mono space-y-1.5">
                    <div className="flex justify-between text-slate-400">
                      <span>Population</span>
                      <span className="text-white font-semibold">{city.pop}</span>
                    </div>
                    <div className="text-[10px] text-cyan-400 truncate">
                      {city.tag}
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-3 border-t border-[#1E334A] flex items-center justify-between text-xs font-mono text-cyan-400 group-hover:text-cyan-300">
                  <span>LAUNCH NODE</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section id="capabilities" className="py-20 px-6 lg:px-12 border-t border-[#1E334A]">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="text-xs font-mono text-purple-400 tracking-widest font-semibold uppercase">
              PLATFORM CAPABILITIES
            </div>
            <h2 className="text-3xl sm:text-4xl font-black font-display uppercase tracking-tight text-white">
              End-to-End Urban Intelligence
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 font-sans">
              Built on uncompromising data honesty: zero hallucination, strict provenance, and explicit fallback indicators.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold font-mono text-white uppercase">7 Domain Agents</h3>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                Deterministic multi-agent orchestrator querying weather, air quality, transit, cost, higher education, healthcare, and places in parallel.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
              <div className="w-10 h-10 rounded-xl bg-purple-950/60 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <BookOpen className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold font-mono text-white uppercase">Authoritative RAG</h3>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                Curated knowledge corpus from government, municipal, and international authorities with strict chunk citation and zero hallucinated claims.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#0B1726] border border-[#1E334A] space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-950/60 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                <DollarSign className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold font-mono text-white uppercase">Global Relocation FX</h3>
              <p className="text-xs text-slate-300 leading-relaxed font-sans">
                Live ECB exchange rates via Frankfurter supporting over 160 global currencies with bidirectional conversion and origin/destination model.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final Call to Action */}
      <section className="py-20 px-6 lg:px-12 border-t border-[#1E334A] bg-gradient-to-b from-[#07111F] to-[#030712] text-center">
        <div className="max-w-3xl mx-auto space-y-6">
          <h2 className="text-3xl sm:text-5xl font-black font-display text-white tracking-tight uppercase">
            The city is constantly changing. <br />
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              UrbanLens helps you understand why.
            </span>
          </h2>
          <p className="text-sm text-slate-300 font-sans max-w-xl mx-auto">
            Experience spatial city exploration, real-time observables, and multi-agent AI intelligence designed for modern global citizens.
          </p>
          <div className="pt-2">
            <Link
              to="/app"
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 hover:from-cyan-400 hover:to-purple-500 text-slate-950 font-mono font-bold text-sm tracking-wider shadow-[0_0_35px_rgba(34,211,238,0.4)] transition-all inline-flex items-center gap-2"
            >
              <span>ENTER THE OPERATING SYSTEM</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Public Footer */}
      <footer className="py-8 px-6 lg:px-12 border-t border-[#1E334A] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <span className="font-bold text-white">URBANLENS AI</span>
          <span>·</span>
          <span>SOURCE-GROUNDED URBAN INTELLIGENCE</span>
        </div>
        <div>
          © 2026 UrbanLens Intelligence Systems. All rights reserved.
        </div>
      </footer>
    </div>
  );
};
