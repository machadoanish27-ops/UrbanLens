import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext.tsx';
import { Mail, ArrowLeft, Send, CheckCircle2 } from 'lucide-react';

export const AuthForgotPassword: React.FC = () => {
  const { navigate } = useUrban();
  const [email, setEmail] = useState('');
  const [isSent, setIsSent] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsSent(true);
    }, 600);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#030712] p-4 sm:p-8 font-sans">
      <div className="absolute inset-0 bg-spatial-grid opacity-35" />

      <div className="relative z-10 w-full max-w-md rounded-3xl bg-[#0B1726]/90 backdrop-blur-xl border border-[#1E334A] p-8 shadow-2xl space-y-6">
        <div className="text-center border-b border-[#1E334A] pb-4">
          <h2 className="text-xl font-bold font-mono text-white uppercase tracking-wider">
            RECOVER CREDENTIALS
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Dispatch single-use cryptographic recovery link
          </p>
        </div>

        {isSent ? (
          <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-center space-y-3">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
            <h3 className="text-sm font-bold text-white font-mono">RECOVERY DISPATCHED</h3>
            <p className="text-xs text-slate-300 font-sans">
              A secure authentication token has been delivered to <span className="text-cyan-400">{email}</span>.
            </p>
            <button
              onClick={() => navigate('login')}
              className="mt-2 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-mono font-bold"
            >
              RETURN TO LOGIN
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-mono text-slate-300 mb-1.5">
                REGISTERED EMAIL ADDRESS
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="v.mehta@urbanlens.gov"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white outline-none"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading || !email}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-xs tracking-wider transition-all flex items-center justify-center gap-2"
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isLoading ? 'DISPATCHING TOKEN...' : 'SEND RESET LINK'}</span>
            </button>
          </form>
        )}

        <div className="text-center pt-2 border-t border-[#1E334A]">
          <button
            onClick={() => navigate('login')}
            className="text-xs font-mono text-slate-400 hover:text-white flex items-center justify-center gap-1.5 mx-auto"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to Login</span>
          </button>
        </div>
      </div>
    </div>
  );
};
