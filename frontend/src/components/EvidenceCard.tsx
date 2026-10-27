import React from 'react';
import { FileText, ExternalLink, Tag } from 'lucide-react';
import type { EvidenceUsedItem, KnowledgeEvidenceItem } from '../types/api';

interface EvidenceCardProps {
  evidence: EvidenceUsedItem | KnowledgeEvidenceItem;
  className?: string;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence, className = '' }) => {
  const isDetailed = 'text' in evidence;
  const detailed = isDetailed ? (evidence as KnowledgeEvidenceItem) : null;
  const claim = 'claim' in evidence ? (evidence as EvidenceUsedItem).claim : null;

  return (
    <div
      className={`glass-panel p-4 rounded-xl border border-slate-800 text-left transition-all hover:border-indigo-500/30 ${className}`}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <h4 className="text-sm font-semibold text-slate-200 truncate" title={evidence.title || 'Evidence'}>
            {evidence.title || 'Evidence Chunk'}
          </h4>
        </div>

        {evidence.source_url && (
          <a
            href={evidence.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1 shrink-0 px-2 py-0.5 rounded bg-indigo-950/40 border border-indigo-800/40"
          >
            <span>Source</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      {evidence.source && (
        <div className="flex items-center gap-2 mb-2 text-xs text-slate-400">
          <span className="font-medium text-slate-300">{evidence.source}</span>
          {detailed?.category && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] bg-slate-800 text-slate-400 border border-slate-700">
              <Tag className="w-2.5 h-2.5" />
              {detailed.category}
            </span>
          )}
        </div>
      )}

      {claim && (
        <p className="text-xs text-slate-300 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80 mb-2 leading-relaxed">
          <strong className="text-indigo-300">Grounding Claim:</strong> {claim}
        </p>
      )}

      {detailed?.text && (
        <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
          "{detailed.text}"
        </p>
      )}
    </div>
  );
};
