import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useUrban } from '../context/UrbanContext';
import { ArrowRight, Lock, Mail, User } from 'lucide-react';

export const AuthSignUp: React.FC = () => {
  const { loginUser } = useUrban();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      loginUser(email || 'new.user@urbanlens.ai', name || 'Urban Explorer');
      navigate('/app');
    }, 400);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#030712] p-4 sm:p-8 font-sans">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-r from-[#030712] via-[#030712]/90 to-[#030712]/70" />
        <div className="absolute inset-0 bg-spatial-grid opacity-30" />
      </div>

      <div className="relative z-10 w-full max-w-lg rounded-3xl bg-[#0B1726]/85 backdrop-blur-xl border border-[#1E334A] p-7 sm:p-8 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-[#1E334A] pb-4">
          <div>
            <h2 className="text-lg font-bold font-mono text-white uppercase tracking-wider">
              CREATE WORKSPACE ACCOUNT
            </h2>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Join the UrbanLens Global Intelligence System
            </p>
          </div>
          <Link to="/login" className="text-xs font-mono text-cyan-400 hover:text-cyan-300">
            Sign In →
          </Link>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[11px] font-mono text-slate-300 mb-1.5">
              FULL NAME
            </label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Dr. Jordan Hayes"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-500 outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono text-slate-300 mb-1.5">
              EMAIL ADDRESS
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jordan.hayes@enterprise.com"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-500 outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono text-slate-300 mb-1.5">
              SECURITY KEY / PASSWORD
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-500 outline-none transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-xs tracking-wider shadow-[0_0_20px_rgba(34,211,238,0.3)] transition-all flex items-center justify-center gap-2"
          >
            <span>{isLoading ? 'CREATING WORKSPACE...' : 'REGISTER WORKSPACE'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-[10px] font-mono text-slate-400 leading-relaxed">
          <span className="text-cyan-400 font-bold">Privacy Note:</span> Workspace profiles and saved city research are stored locally in client storage. No passwords are transmitted to third parties.
        </div>
      </div>
    </div>
  );
};
