import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  Send,
  ShieldCheck,
  AlertTriangle,
  Cpu,
  Clock,
  Lightbulb,
  CheckCircle2,
  FileText,
} from 'lucide-react';
import { useAskIntelligence, useCities } from '../hooks/useUrbanLens';
import { EvidenceCard } from '../components/EvidenceCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

const EXAMPLE_QUERIES = [
  { text: 'What is the current air quality and living environment in Tokyo?', cityId: 'city_1392685764' },
  { text: 'Is London or Paris more affordable for university students?', cityId: 'city_1826645935' },
  { text: 'What are the main public transport options and population metrics in Mumbai?', cityId: 'city_1356226629' },
  { text: 'Give me an overview of tech opportunities, cost, and climate in New York.', cityId: 'city_1840034016' },
];

export const AskPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQ = searchParams.get('q') || '';
  const initialCityId = searchParams.get('cityId') || '';

  const [query, setQuery] = useState(initialQ);
  const [selectedCityId, setSelectedCityId] = useState(initialCityId);

  const { data: citiesData } = useCities({ page_size: 20 });
  const cities = citiesData?.data || [];

  const askMutation = useAskIntelligence();

  // If query and cityId came from URL, automatically run once
  useEffect(() => {
    if (initialQ && !askMutation.data && !askMutation.isPending && !askMutation.error) {
      askMutation.mutate({
        query: initialQ,
        city_id: initialCityId || undefined,
      });
    }
  }, [initialQ, initialCityId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSearchParams({
      q: query.trim(),
      ...(selectedCityId ? { cityId: selectedCityId } : {}),
    });

    askMutation.mutate({
      query: query.trim(),
      city_id: selectedCityId.trim() || undefined,
    });
  };

  const handleSelectExample = (ex: { text: string; cityId: string }) => {
    setQuery(ex.text);
    setSelectedCityId(ex.cityId);
    setSearchParams({ q: ex.text, cityId: ex.cityId });
    askMutation.mutate({
      query: ex.text,
      city_id: ex.cityId,
    });
  };

  const response = askMutation.data?.data;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Grounded Multi-Agent LLM Reasoning</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Ask UrbanLens Intelligence
        </h1>
        <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
          Ask questions about any city. Responses are strictly grounded in real MongoDB Atlas records, live sensors, and dense RAG citations.
        </p>
      </div>

      {/* Query Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* City Scope Selector */}
          <div className="sm:w-64 shrink-0">
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">
              City Focus (Optional)
            </label>
            <select
              value={selectedCityId}
              onChange={(e) => setSelectedCityId(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Cities / Global</option>
              {cities.map((c) => (
                <option key={c.city_id} value={c.city_id}>
                  {c.name} ({c.country_iso2})
                </option>
              ))}
              {!cities.some((c) => c.city_id === selectedCityId) && selectedCityId && (
                <option value={selectedCityId}>{selectedCityId}</option>
              )}
            </select>
          </div>

          {/* Question Text Input */}
          <div className="flex-1">
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">
              Your Question
            </label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Compare the air quality and transit infrastructure of Tokyo..."
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          <span className="text-[11px] text-slate-500 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Zero-Hallucination Policy: Backed by citations
          </span>

          <button
            type="submit"
            disabled={askMutation.isPending || !query.trim()}
            className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
          >
            {askMutation.isPending ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Reasoning with Groq...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5" />
                <span>Submit Inquiry</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* Suggested Prompts */}
      {!response && !askMutation.isPending && (
        <div className="space-y-3">
          <span className="text-xs font-semibold text-slate-400 block">
            Suggested Intelligence Prompts:
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {EXAMPLE_QUERIES.map((ex, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectExample(ex)}
                className="glass-panel p-3.5 rounded-xl text-left border border-slate-800/80 hover:border-indigo-500/40 text-xs text-slate-300 transition-all flex items-center justify-between group"
              >
                <span className="line-clamp-1">{ex.text}</span>
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0 ml-2 group-hover:scale-110 transition-transform" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {askMutation.isPending && (
        <div className="glass-panel p-8 rounded-3xl border border-indigo-500/30 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center mx-auto animate-pulse">
            <Cpu className="w-6 h-6 animate-spin" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Synthesizing Grounded Intelligence</h3>
            <p className="text-xs text-slate-400 mt-1">
              Querying 7 domain agents → Retrieving dense vector evidence chunks → Formulating grounded reasoning via Groq LLM...
            </p>
          </div>
          <LoadingSkeleton count={2} height="h-20" />
        </div>
      )}

      {/* Error State */}
      {askMutation.isError && (
        <div className="glass-panel p-6 rounded-2xl border border-rose-500/40 bg-rose-950/20 text-left space-y-3">
          <div className="flex items-center gap-2 text-rose-400">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <h3 className="text-sm font-bold">Failed to generate intelligence response</h3>
          </div>
          <p className="text-xs text-slate-300">
            {askMutation.error?.message || 'Server returned an error. Ensure the FastAPI backend and Groq LLM service are active.'}
          </p>
        </div>
      )}

      {/* Response Display */}
      {response && (
        <div className="space-y-6">
          {/* Main Answer Card */}
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/30 bg-slate-900/40 shadow-2xl space-y-6">
            {/* Header / City Tag */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {response.city_name || response.city_id}
                </span>
                {response.country && (
                  <span className="text-xs text-slate-400">{response.country}</span>
                )}
              </div>

              {/* Groq LLM Telemetry Pill */}
              {response.llm && (
                <div className="flex items-center gap-3 text-[11px] text-slate-400 bg-slate-950/80 px-3 py-1.5 rounded-full border border-slate-800">
                  <span className="flex items-center gap-1 font-mono text-indigo-300">
                    <Cpu className="w-3 h-3 text-indigo-400" />
                    {response.llm.model}
                  </span>
                  <span className="flex items-center gap-1 text-slate-500 border-l border-slate-800 pl-2">
                    <Clock className="w-3 h-3" />
                    {response.llm.latency_ms}ms
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400 border-l border-slate-800 pl-2">
                    <CheckCircle2 className="w-3 h-3" />
                    Confidence: {Math.round(response.confidence * 100)}%
                  </span>
                </div>
              )}
            </div>

            {/* Grounded Answer Text */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Grounded Assessment
              </h3>
              <div className="text-slate-100 text-sm sm:text-base leading-relaxed whitespace-pre-line font-normal">
                {response.answer}
              </div>
            </div>

            {/* Recommendation Highlight */}
            {response.recommendation && (
              <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 to-indigo-950/40 border border-emerald-500/30 flex items-start gap-3">
                <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 shrink-0">
                  <Lightbulb className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">
                    Recommendation & Actionable Insight
                  </h4>
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                    {response.recommendation}
                  </p>
                </div>
              </div>
            )}

            {/* Key Points */}
            {response.key_points && response.key_points.length > 0 && (
              <div className="space-y-2 pt-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Key Takeaways
                </h4>
                <ul className="space-y-2">
                  {response.key_points.map((pt, idx) => (
                    <li
                      key={idx}
                      className="text-xs sm:text-sm text-slate-200 flex items-start gap-2.5"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2 shrink-0" />
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Warnings banner */}
            {response.warnings && response.warnings.length > 0 && (
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <strong>Data Limitations & Warnings:</strong>
                  <ul className="list-disc list-inside mt-1 space-y-0.5 text-amber-200">
                    {response.warnings.map((w, wIdx) => (
                      <li key={wIdx}>{w}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Sources list */}
            {response.sources && response.sources.length > 0 && (
              <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
                <span className="text-xs font-semibold text-slate-400">Sources:</span>
                {response.sources.map((src, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded text-[11px] bg-slate-900 border border-slate-800 text-slate-300"
                  >
                    {src}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Evidence Chunks Used */}
          {response.evidence_used && response.evidence_used.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">
                  Evidence Chunks Grounding this Response ({response.evidence_used.length})
                </h3>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {response.evidence_used.map((ev, idx) => (
                  <EvidenceCard key={idx} evidence={ev} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
