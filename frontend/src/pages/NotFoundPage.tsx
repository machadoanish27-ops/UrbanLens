import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, AlertTriangle } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center max-w-lg mx-auto my-16 space-y-4">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h1 className="text-3xl font-extrabold text-white">404 - Page Not Found</h1>
      <p className="text-sm text-slate-400">
        The requested urban intelligence route does not exist in UrbanLens.
      </p>
      <div className="pt-4">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30"
        >
          <Compass className="w-4 h-4" />
          <span>Return to Exploration</span>
        </Link>
      </div>
    </div>
  );
};
