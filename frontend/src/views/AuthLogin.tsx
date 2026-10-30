import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext.tsx';
import { ArrowRight, Lock, Mail, Activity, ShieldCheck, Sparkles } from 'lucide-react';

export const AuthLogin: React.FC = () => {
  const { navigate, loginUser } = useUrban();
  const [email, setEmail] = useState('v.mehta@urbanlens.gov');
  const [password, setPassword] = useState('••••••••••••');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      loginUser(email);
    }, 700);
  };

  const handleDemoSignIn = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      loginUser('demo.operator@urbanlens.gov');
    }, 400);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#030712] p-4 sm:p-8 font-sans">
      {/* Background City Visualization */}
      <div className="absolute inset-0 z-0">
        <img
          src="/src/assets/images/hero_digital_city_1793341279762.jpg"
          alt="UrbanLens Digital City"
          className="w-full h-full object-cover opacity-25 filter brightness-70 scale-105"
          referrerPolicy="no-referrer"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#030712] via-[#030712]/80 to-[#030712]/60" />
        <div className="absolute inset-0 bg-spatial-grid opacity-35" />
      </div>

      <div className="relative z-10 w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Branding Column */}
        <div className="lg:col-span-7 space-y-6 text-left">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 p-[1px] shadow-[0_0_20px_rgba(34,211,238,0.3)]">
              <div className="w-full h-full bg-[#030712] rounded-xl flex items-center justify-center">
                <span className="font-mono font-black text-cyan-400 text-base">UL</span>
              </div>
            </div>
            <div>
              <div className="text-xl font-black tracking-widest font-display text-white">
                URBANLENS
              </div>
              <div className="text-[10px] font-mono tracking-widest text-slate-400">
                URBAN INTELLIGENCE PLATFORM
              </div>
            </div>
          </div>

          <h1 className="text-4xl sm:text-5xl font-black font-display text-white tracking-tight uppercase leading-tight">
            See the city. <br />
            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Understand the city.
            </span> <br />
            Shape the future.
          </h1>

          <p className="text-sm text-slate-300 font-sans max-w-lg leading-relaxed">
            Enterprise command access to spatial twins, real-time sensor ingestion,
            multimodal AI intelligence, and particle swarm corridor optimization.
          </p>

          <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
              FEDRAMP / ISO 27001 SECURE
            </span>
            <span>·</span>
            <span>RESTRICTED ACCESS LEVEL 4</span>
          </div>
        </div>

        {/* Right Glass Authentication Panel */}
        <div className="lg:col-span-5 rounded-3xl bg-[#0B1726]/80 backdrop-blur-xl border border-[#1E334A] p-8 shadow-2xl space-y-6">
          <div className="border-b border-[#1E334A] pb-4">
            <h2 className="text-lg font-bold font-mono text-white uppercase tracking-wider">
              OPERATOR SIGN IN
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Enter municipal operations credentials
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-mono text-slate-300 mb-1.5">
                OPERATIONAL EMAIL
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[11px] font-mono text-slate-300">
                  SECURITY KEY / PASSWORD
                </label>
                <button
                  type="button"
                  onClick={() => navigate('forgot-password')}
                  className="text-[11px] font-mono text-cyan-400 hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white outline-none transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-xs tracking-wider shadow-[0_0_20px_rgba(34,211,238,0.3)] transition-all flex items-center justify-center gap-2"
            >
              <span>{isLoading ? 'AUTHENTICATING TELEMETRY...' : 'SIGN IN'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Alternative Quick Sign-In */}
          <div className="space-y-3 pt-2 border-t border-[#1E334A]">
            <button
              onClick={handleDemoSignIn}
              type="button"
              className="w-full py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-slate-200 text-xs font-mono font-semibold transition-colors flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>CONTINUE WITH GOOGLE WORKSPACE</span>
            </button>

            <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-1">
              <span>New command personnel?</span>
              <button
                onClick={() => navigate('signup')}
                className="text-cyan-400 hover:underline font-semibold"
              >
                Create Account
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Status Ticker per Section 3 */}
      <div className="absolute bottom-4 left-0 right-0 z-10 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#07111F]/90 border border-[#1E334A] text-[11px] font-mono text-emerald-400">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>● SYSTEM STATUS — ALL INTELLIGENCE SYSTEMS OPERATIONAL</span>
        </div>
      </div>
    </div>
  );
};
