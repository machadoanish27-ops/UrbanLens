import React from 'react';
import { ShieldCheck, Calendar, ExternalLink } from 'lucide-react';

interface ProvenanceTagProps {
  source?: string | null;
  observedAt?: string | null;
  confidence?: number | null;
  className?: string;
  sourceUrl?: string | null;
}

export const ProvenanceTag: React.FC<ProvenanceTagProps> = ({
  source,
  observedAt,
  confidence,
  className = '',
  sourceUrl,
}) => {
  if (!source && !observedAt && confidence === undefined) return null;

  return (
    <div className={`flex flex-wrap items-center gap-2 text-xs text-slate-400 ${className}`}>
      {source && (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
          <ShieldCheck className="w-3 h-3 text-indigo-400" />
          <span>Source: <strong className="font-medium text-slate-200">{source}</strong></span>
          {sourceUrl && (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-1 text-indigo-400 hover:text-indigo-300"
              title="View source"
            >
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </span>
      )}

      {confidence !== undefined && confidence !== null && (
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-medium ${
            confidence >= 0.8
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : confidence >= 0.5
              ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
          }`}
        >
          Confidence: {Math.round(confidence * 100)}%
        </span>
      )}

      {observedAt && (
        <span className="inline-flex items-center gap-1 text-slate-500">
          <Calendar className="w-3 h-3" />
          <span>{new Date(observedAt).toLocaleDateString()}</span>
        </span>
      )}
    </div>
  );
};
