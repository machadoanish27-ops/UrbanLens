import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { useAskIntelligence } from '../hooks/useUrbanLens';
import { DataTrustBadge } from '../components/common/DataTrustBadge';
import { EvidenceCard } from '../components/EvidenceCard';
import type { LLMAskResponse } from '../types/api';
import {
  Sparkles,
  Send,
  RotateCcw,
  CheckCircle2,
  Lightbulb,
  Cpu,
  Clock,
} from 'lucide-react';

const SUGGESTED_QUERIES = [
  'What is the current air quality and living environment?',
  'What are the typical rental costs and cost of living breakdown?',
  'What accredited universities and colleges are in this city?',
  'What are the public transit options and commute infrastructure?',
  'Compare safety, healthcare, and cost of living for relocation.',
];

export const AiIntelligencePage: React.FC = () => {
  const { currentCity, activeCityId } = useUrban();
  const [query, setQuery] = useState('');
  const [activeResponse, setActiveResponse] = useState<LLMAskResponse | null>(null);

  const askMutation = useAskIntelligence();

  const handleRunQuery = (promptText: string) => {
    const q = promptText.trim();
    if (!q || askMutation.isPending) return;

    setQuery(q);
    askMutation.mutate(
      {
        query: q,
        city_id: activeCityId,
      },
      {
        onSuccess: (data) => {
          if (data?.data) {
            setActiveResponse(data.data);
          }
        },
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6 shadow-xl">
        <div>
          <div className="text-xs font-mono text-purple-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span>NEURAL SPATIAL REASONING ENGINE</span>
            <span>·</span>
            <DataTrustBadge status="INFERENCE" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            AI Operational Intelligence
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Causal multi-agent inference synthesizing live weather, air quality, Numbeo economics, OpenStreetMap POIs, and authoritative RAG documents for <strong className="text-white font-mono">{currentCity.name}</strong>.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-3 py-1.5 rounded-xl bg-purple-950/60 border border-purple-500/40 text-purple-300 font-bold">
            GROQ LLAMA-3.3-70B
          </span>
        </div>
      </div>

      {/* Query Bar */}
      <div className="rounded-2xl bg-[#0B1726] border border-[#1E334A] p-4 shadow-xl space-y-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleRunQuery(query);
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Ask anything about ${currentCity.name} (e.g. rent costs, healthcare, visa rules, climate)...`}
            className="w-full pl-4 pr-28 py-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] focus:border-cyan-400 text-xs sm:text-sm font-mono text-white placeholder-slate-400 outline-none transition-colors"
          />
          <button
            type="submit"
            disabled={askMutation.isPending || !query.trim()}
            className="absolute right-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-40 text-slate-950 font-mono font-bold text-xs flex items-center gap-1.5 transition-all shadow-md"
          >
            {askMutation.isPending ? (
              <>
                <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                <span>REASONING...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>QUERY</span>
              </>
            )}
          </button>
        </form>

        {/* Suggested Prompts */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
            <Lightbulb className="w-3 h-3 text-amber-400" /> SUGGESTED:
          </span>
          {SUGGESTED_QUERIES.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => handleRunQuery(sq)}
              className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-slate-300 hover:text-white transition-colors"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Response Panel */}
      {activeResponse ? (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Main Answer Card */}
          <div className="p-6 rounded-2xl bg-[#0B1726] border border-cyan-500/40 space-y-4 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1E334A] pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                  AI SYNTHESIZED REASONING
                </h3>
              </div>

              <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
                <span className="flex items-center gap-1">
                  <Cpu className="w-3 h-3 text-cyan-400" /> {activeResponse.llm?.model || 'LLaMA-3.3-70B'}
                </span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-emerald-400" /> {activeResponse.llm?.latency_ms || 240}ms
                </span>
                <span>·</span>
                <span className="text-emerald-400 font-bold">
                  {Math.round(activeResponse.confidence * 100)}% CONFIDENCE
                </span>
              </div>
            </div>

            {/* Answer Text */}
            <div className="text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
              {activeResponse.answer}
            </div>

            {/* Key Points */}
            {activeResponse.key_points && activeResponse.key_points.length > 0 && (
              <div className="pt-3 border-t border-[#1E334A] space-y-2">
                <div className="text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">
                  KEY ACTIONABLE FINDINGS
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {activeResponse.key_points.map((kp, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs font-mono text-slate-200 flex items-start gap-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{kp}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendation */}
            {activeResponse.recommendation && (
              <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 text-xs font-mono text-slate-200">
                <span className="text-[10px] font-bold text-purple-300 uppercase block mb-1">
                  TACTICAL RELOCATION RECOMMENDATION
                </span>
                <p>{activeResponse.recommendation}</p>
              </div>
            )}
          </div>

          {/* Evidence Cards Grid */}
          {activeResponse.evidence_used && activeResponse.evidence_used.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold font-mono text-white uppercase tracking-wider">
                AUTHORITATIVE RAG CITATIONS & EVIDENCE ({activeResponse.evidence_used.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activeResponse.evidence_used.map((ev, idx) => (
                  <EvidenceCard key={idx} evidence={ev} />
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Empty / Idle State */
        <div className="p-12 rounded-3xl bg-[#0B1726]/60 border border-[#1E334A] text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-cyan-950/40 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-8 h-8" />
          </div>
          <h2 className="text-lg font-bold font-mono text-white uppercase tracking-wider">
            AWAITING REASONING DIRECTIVE
          </h2>
          <p className="text-xs text-slate-400 font-mono max-w-md mx-auto">
            Submit a relocation question above or select a suggested prompt to engage the multi-agent neural synthesis engine.
          </p>
        </div>
      )}
    </div>
  );
};
