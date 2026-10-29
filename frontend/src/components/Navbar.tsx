import React, { useState } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  Columns2,
  Menu,
  X,
  Database,
  Activity,
  Search,
} from 'lucide-react';
import { useDbHealth, useHealth } from '../hooks/useUrbanLens';
import { CurrencyWidget } from './CurrencyWidget';

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [quickSearch, setQuickSearch] = useState('');
  const navigate = useNavigate();

  const { data: health, isSuccess: healthOk } = useHealth();
  const { data: dbHealth, isSuccess: dbOk } = useDbHealth();

  const isSystemHealthy = healthOk && dbOk && health?.status === 'ok';

  const handleQuickSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickSearch.trim()) {
      navigate(`/?q=${encodeURIComponent(quickSearch.trim())}`);
      setQuickSearch('');
      setMobileMenuOpen(false);
    }
  };

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
        : 'text-slate-300 hover:text-white hover:bg-slate-900/60'
    }`;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 shrink-0 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-400 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Compass className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg tracking-tight text-white group-hover:text-indigo-300 transition-colors">
                  UrbanLens
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  v1.0
                </span>
              </div>
              <p className="text-[10px] text-slate-400 -mt-0.5 hidden sm:block">
                Source-Grounded City Intelligence
              </p>
            </div>
          </Link>

          {/* Quick Search */}
          <form
            onSubmit={handleQuickSearch}
            className="hidden md:flex items-center relative flex-1 max-w-xs"
          >
            <Search className="w-4 h-4 absolute left-3 text-slate-500 pointer-events-none" />
            <input
              type="text"
              value={quickSearch}
              onChange={(e) => setQuickSearch(e.target.value)}
              placeholder="Find any city (e.g. Tokyo)..."
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg bg-slate-900/90 border border-slate-800 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </form>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center gap-1.5">
            <NavLink to="/" end className={navLinkClass}>
              <Compass className="w-4 h-4" />
              <span>Explore Cities</span>
            </NavLink>

            <NavLink to="/ask" className={navLinkClass}>
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Ask AI Intelligence</span>
            </NavLink>

            <NavLink to="/compare" className={navLinkClass}>
              <Columns2 className="w-4 h-4" />
              <span>Compare</span>
            </NavLink>
          </nav>

          {/* Global Live Currency Widget */}
          <div className="flex items-center">
            <CurrencyWidget />
          </div>

          {/* Live System Status Pill */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                isSystemHealthy
                  ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)] animate-pulse'
                  : 'bg-amber-400'
              }`}
            />
            <span className="text-slate-300 font-medium">
              {isSystemHealthy ? 'System Active' : 'Connecting...'}
            </span>
            {dbHealth?.latency_ms !== undefined && (
              <span className="text-slate-500 text-[11px] border-l border-slate-800 pl-2">
                Atlas {Math.round(dbHealth.latency_ms)}ms
              </span>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-800/80 space-y-2">
            <form onSubmit={handleQuickSearch} className="relative mb-3">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500 pointer-events-none" />
              <input
                type="text"
                value={quickSearch}
                onChange={(e) => setQuickSearch(e.target.value)}
                placeholder="Search canonical cities..."
                className="w-full pl-9 pr-3 py-2 text-sm rounded-lg bg-slate-900 border border-slate-800 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </form>

            <NavLink
              to="/"
              end
              onClick={() => setMobileMenuOpen(false)}
              className={navLinkClass}
            >
              <Compass className="w-4 h-4" />
              <span>Explore Cities</span>
            </NavLink>

            <NavLink
              to="/ask"
              onClick={() => setMobileMenuOpen(false)}
              className={navLinkClass}
            >
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span>Ask AI Intelligence</span>
            </NavLink>

            <NavLink
              to="/compare"
              onClick={() => setMobileMenuOpen(false)}
              className={navLinkClass}
            >
              <Columns2 className="w-4 h-4" />
              <span>Compare Cities</span>
            </NavLink>

            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400 px-3">
              <span className="flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-400" />
                Backend: {health?.service || 'UrbanLens'}
              </span>
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-indigo-400" />
                DB: {dbHealth?.connected ? 'Atlas Connected' : 'Checking'}
              </span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};
