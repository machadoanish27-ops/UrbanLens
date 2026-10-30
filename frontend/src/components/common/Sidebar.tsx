import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useUrban } from '../../context/UrbanContext';
import {
  LayoutDashboard,
  Compass,
  Map as MapIcon,
  Scale,
  Sparkles,
  CloudSun,
  Wind,
  Car,
  Coins,
  Home,
  GraduationCap,
  HeartPulse,
  ShieldAlert,
  Coffee,
  Bookmark,
  Briefcase,
  DollarSign,
  BookOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onCloseMobile?: () => void;
}

interface NavItem {
  to: string;
  label: string;
  icon: React.ElementType;
  badge?: string;
  badgeColor?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggleCollapse, onCloseMobile }) => {
  const { savedCities } = useUrban();

  const sections: NavSection[] = [
    {
      title: 'EXPLORE',
      items: [
        { to: '/app', label: 'Discover', icon: LayoutDashboard },
        { to: '/app/map', label: 'Global Map', icon: MapIcon, badge: 'MAP' },
        { to: '/app/explore', label: 'Cities', icon: Compass },
        { to: '/app/compare', label: 'Compare', icon: Scale },
      ],
    },
    {
      title: 'INTELLIGENCE',
      items: [
        { to: '/app/ask', label: 'Ask AI', icon: Sparkles, badge: 'AI', badgeColor: 'bg-purple-900/60 text-purple-300' },
        { to: '/app/weather', label: 'Weather', icon: CloudSun },
        { to: '/app/air-quality', label: 'Air Quality', icon: Wind },
        { to: '/app/mobility', label: 'Mobility & Transit', icon: Car },
        { to: '/app/cost', label: 'Cost of Living', icon: Coins },
        { to: '/app/housing', label: 'Housing', icon: Home },
        { to: '/app/education', label: 'Education', icon: GraduationCap },
        { to: '/app/healthcare', label: 'Healthcare', icon: HeartPulse },
        { to: '/app/safety', label: 'Safety & Essentials', icon: ShieldAlert },
        { to: '/app/lifestyle', label: 'Lifestyle & POIs', icon: Coffee },
      ],
    },
    {
      title: 'PERSONAL',
      items: [
        { to: '/app/workspace', label: 'Workspace', icon: Briefcase },
        {
          to: '/app/saved',
          label: 'Saved',
          icon: Bookmark,
          badge: savedCities.length > 0 ? `${savedCities.length}` : undefined,
          badgeColor: 'bg-cyan-900/60 text-cyan-300',
        },
      ],
    },
    {
      title: 'SYSTEM',
      items: [
        { to: '/app/currency', label: 'Currency & FX', icon: DollarSign },
        { to: '/app/knowledge', label: 'Knowledge Base', icon: BookOpen, badge: 'RAG' },
        { to: '/app/settings', label: 'Settings', icon: Settings },
      ],
    },
  ];

  return (
    <aside
      className={`h-screen sticky top-0 bg-[#07111F] border-r border-[#1E334A] flex flex-col justify-between transition-all duration-300 z-30 select-none ${
        isCollapsed ? 'w-[72px]' : 'w-[260px]'
      }`}
    >
      {/* Top Header / Brand Logo */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-[#1E334A] shrink-0">
        {!isCollapsed ? (
          <Link
            to="/app"
            onClick={onCloseMobile}
            className="flex items-center gap-2.5 group"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 p-[1px] shadow-[0_0_15px_rgba(34,211,238,0.3)]">
              <div className="w-full h-full bg-[#030712] rounded-lg flex items-center justify-center">
                <span className="font-mono font-extrabold text-cyan-400 text-sm tracking-tighter">UL</span>
              </div>
            </div>
            <div>
              <div className="text-base font-extrabold tracking-wider font-display text-white group-hover:text-cyan-300 transition-colors">
                URBANLENS
              </div>
              <div className="text-[9px] font-mono tracking-widest text-slate-400">
                AI CITY INTELLIGENCE
              </div>
            </div>
          </Link>
        ) : (
          <Link
            to="/app"
            onClick={onCloseMobile}
            className="w-10 h-10 mx-auto rounded-lg bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 p-[1px] flex items-center justify-center"
          >
            <div className="w-full h-full bg-[#030712] rounded-lg flex items-center justify-center">
              <span className="font-mono font-extrabold text-cyan-400 text-sm">UL</span>
            </div>
          </Link>
        )}

        <button
          onClick={onToggleCollapse}
          className="hidden md:flex p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#0B1726] border border-transparent hover:border-[#1E334A] transition-colors"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links Scroll Container */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6 scrollbar-thin">
        {sections.map((section) => (
          <div key={section.title} className="space-y-1">
            {!isCollapsed && (
              <div className="px-3 text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-widest mb-1.5">
                {section.title}
              </div>
            )}

            {section.items.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/app'}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    `group relative flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-mono font-medium transition-all duration-200 ${
                      isActive
                        ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/40 shadow-[0_0_15px_rgba(34,211,238,0.15)]'
                        : 'text-slate-300 hover:text-white hover:bg-[#0B1726] border border-transparent hover:border-[#1E334A]'
                    }`
                  }
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-110" />

                  {!isCollapsed && (
                    <span className="truncate flex-1 tracking-wide">{item.label}</span>
                  )}

                  {!isCollapsed && item.badge && (
                    <span
                      className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border border-current ${
                        item.badgeColor || 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}

                  {/* Tooltip on collapse */}
                  {isCollapsed && (
                    <div className="hidden group-hover:block fixed left-20 bg-[#0B1726] text-white border border-[#1E334A] rounded-lg px-2.5 py-1 text-xs font-mono shadow-2xl z-50 whitespace-nowrap">
                      {item.label}
                    </div>
                  )}
                </NavLink>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer / Public Link */}
      <div className="p-3 border-t border-[#1E334A] shrink-0 space-y-2">
        <Link
          to="/"
          className="flex items-center justify-center gap-2 p-2 rounded-xl text-xs font-mono text-slate-400 hover:text-cyan-300 hover:bg-[#0B1726] border border-transparent hover:border-[#1E334A] transition-colors"
          title="Return to Public Landing Page"
        >
          <ExternalLink className="w-3.5 h-3.5 shrink-0" />
          {!isCollapsed && <span>Public Landing</span>}
        </Link>
      </div>
    </aside>
  );
};
