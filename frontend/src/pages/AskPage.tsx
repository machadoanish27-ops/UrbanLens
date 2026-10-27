import { useState, useEffect, useRef } from 'react';
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
  Copy,
  Check,
  RotateCcw,
  MessageSquare,
  ArrowRight,
  Database,
} from 'lucide-react';
import { useAskIntelligence, useCities } from '../hooks/useUrbanLens';
import { EvidenceCard } from '../components/EvidenceCard';
import type { LLMAskResponse } from '../types/api';

const EXAMPLE_QUERIES = [
  { text: 'What is the current air quality and living environment in Tokyo?', cityId: 'city_1392685764' },
  { text: 'Is London or Paris more affordable for university students?', cityId: 'city_1826645935' },
  { text: 'What are the main public transport options and population metrics in Mumbai?', cityId: 'city_1356226629' },
  { text: 'Give me an overview of tech opportunities, cost, and climate in New York.', cityId: 'city_1840034016' },
];

const FOLLOWUP_PROMPTS = [
  'What are the public transit options and commute times?',
  'What is the typical rental cost and cost of living breakdown?',
  'What ranked universities are in or near this metropolitan area?',
  'How does air quality compare against WHO guidelines?',
];

interface ConversationTurn {
  id: string;
  query: string;
  cityId?: string;
  cityName?: string;
  response?: LLMAskResponse;
  error?: string;
  timestamp: string;
}

export const AskPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQ = searchParams.get('q') || '';
  const initialCityId = searchParams.get('cityId') || '';

  const [query, setQuery] = useState(initialQ);
  const [selectedCityId, setSelectedCityId] = useState(initialCityId);
  const [conversation, setConversation] = useState<ConversationTurn[]>([]);
  const [copiedTurnId, setCopiedTurnId] = useState<string | null>(null);

  const threadBottomRef = useRef<HTMLDivElement>(null);

  const { data: citiesData } = useCities({ page_size: 30 });
  const cities = citiesData?.data || [];

  const askMutation = useAskIntelligence();

  // If query and cityId came from URL, automatically run once
  useEffect(() => {
    if (initialQ && conversation.length === 0 && !askMutation.isPending) {
      handleExecuteQuery(initialQ, initialCityId || undefined);
    }
  }, [initialQ, initialCityId]);

  const handleExecuteQuery = (promptText: string, targetCityId?: string) => {
    const q = promptText.trim();
    if (!q) return;

    const turnId = `turn_${Date.now()}`;
    const targetCity = cities.find((c) => c.city_id === targetCityId);

    // Optimistically push user question turn
    const newTurn: ConversationTurn = {
      id: turnId,
      query: q,
      cityId: targetCityId,
      cityName: targetCity?.name,
      timestamp: new Date().toLocaleTimeString(),
    };

    setConversation((prev) => [...prev, newTurn]);
    setQuery('');

    // Update query params
    setSearchParams({
      q,
      ...(targetCityId ? { cityId: targetCityId } : {}),
    });

    // Execute through FastAPI Groq endpoint
    askMutation.mutate(
      {
        query: q,
        city_id: targetCityId || undefined,
      },
      {
        onSuccess: (data) => {
          setConversation((prev) =>
            prev.map((t) =>
              t.id === turnId
                ? {
                    ...t,
                    response: data.data,
                    cityName: data.data.city_name || t.cityName,
                  }
                : t
            )
          );
          setTimeout(() => {
            threadBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        },
        onError: (err) => {
          setConversation((prev) =>
            prev.map((t) =>
              t.id === turnId
                ? {
                    ...t,
                    error: err.message || 'Failed to synthesize grounded intelligence response.',
                  }
                : t
            )
          );
        },
      }
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || askMutation.isPending) return;
    handleExecuteQuery(query, selectedCityId.trim() || undefined);
  };

  const handleClearConversation = () => {
    setConversation([]);
    setSearchParams({});
    setQuery('');
  };

  const handleCopyAnswer = (turnId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedTurnId(turnId);
    setTimeout(() => setCopiedTurnId(null), 2500);
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Multi-Turn Grounded AI Reasoning Console</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          Ask UrbanLens Intelligence
        </h1>
        <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
          Ask single or follow-up questions about any city. Every claim is strictly grounded in real MongoDB Atlas records, live sensors, and dense RAG citations.
        </p>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleSubmit} className="glass-panel p-5 rounded-3xl border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* City Scope Selector */}
          <div className="sm:w-64 shrink-0">
            <label htmlFor="city-select" className="block text-xs font-semibold text-slate-400 mb-1.5">
              City Focus
            </label>
            <select
              id="city-select"
              value={selectedCityId}
              onChange={(e) => setSelectedCityId(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 focus-visible:ring-2 focus-visible:ring-indigo-500"
            >
              <option value="">All Cities / Global Scope</option>
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
            <label htmlFor="question-input" className="block text-xs font-semibold text-slate-400 mb-1.5">
              Your Inquiry
            </label>
            <div className="relative">
              <input
                id="question-input"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about weather, air quality, transit, rent, universities, or safety..."
                className="w-full pl-4 pr-10 py-2.5 rounded-xl bg-slate-900 border border-slate-700/80 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus-visible:ring-2 focus-visible:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={askMutation.isPending || !query.trim()}
                className="absolute right-1.5 top-1.5 p-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white transition-colors"
                aria-label="Submit Question"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs">
          <span className="text-[11px] text-slate-500 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Zero-Hallucination Policy: Backed by citations & telemetry
          </span>

          <div className="flex items-center gap-2">
            {conversation.length > 0 && (
              <button
                type="button"
                onClick={handleClearConversation}
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors"
                title="Clear conversation history"
              >
                <RotateCcw className="w-3 h-3" />
                <span>New Session</span>
              </button>
            )}

            <button
              type="submit"
              disabled={askMutation.isPending || !query.trim()}
              className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-1.5"
            >
              {askMutation.isPending ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Reasoning with Groq...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Synthesize Answer</span>
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Suggested Prompts (when no conversation started yet) */}
      {conversation.length === 0 && !askMutation.isPending && (
        <div className="space-y-3">
          <span className="text-xs font-semibold text-slate-400 block">
            Suggested Authoritative Intelligence Inquiries:
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {EXAMPLE_QUERIES.map((ex, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setSelectedCityId(ex.cityId);
                  handleExecuteQuery(ex.text, ex.cityId);
                }}
                className="glass-panel p-3.5 rounded-xl text-left border border-slate-800/80 hover:border-indigo-500/40 text-xs text-slate-300 transition-all flex items-center justify-between group"
              >
                <span className="line-clamp-1">{ex.text}</span>
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0 ml-2 group-hover:scale-110 transition-transform" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Conversation Thread */}
      <div className="space-y-8">
        {conversation.map((turn, tIdx) => (
          <article
            key={turn.id}
            aria-label={`Inquiry Turn ${tIdx + 1}`}
            className="space-y-4"
          >
            {/* User Question Bubble */}
            <div className="flex items-start gap-3 justify-end">
              <div className="max-w-2xl bg-indigo-600/20 border border-indigo-500/30 text-white rounded-2xl rounded-tr-sm p-4 text-sm leading-relaxed shadow-lg">
                <div className="flex items-center gap-2 mb-1 text-[11px] font-semibold text-indigo-300">
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Question {tIdx + 1}</span>
                  {turn.cityName && (
                    <span className="px-1.5 py-0.2 rounded bg-indigo-500/30 text-white text-[10px]">
                      {turn.cityName}
                    </span>
                  )}
                  <span className="text-slate-500 text-[10px] ml-auto">{turn.timestamp}</span>
                </div>
                <p className="text-slate-100">{turn.query}</p>
              </div>
            </div>

            {/* AI Response Card or Pending State */}
            {!turn.response && !turn.error ? (
              <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/30 text-left space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center animate-pulse">
                    <Cpu className="w-5 h-5 animate-spin" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">Synthesizing Multi-Source Intelligence</h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Executing domain agents and grounding with dense RAG citations...
                    </p>
                  </div>
                </div>

                {/* Progressive 3-Stage Progress Indicator */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2 text-indigo-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>1. Domain Agents Dispatched</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-2 text-indigo-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>2. Dense RAG Vectors Retrieved</span>
                  </div>
                  <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-600/40 flex items-center gap-2 text-indigo-200 animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping shrink-0" />
                    <span>3. Groq LLM Synthesizing</span>
                  </div>
                </div>
              </div>
            ) : turn.error ? (
              <div className="glass-panel p-6 rounded-2xl border border-rose-500/40 bg-rose-950/20 text-left space-y-2">
                <div className="flex items-center gap-2 text-rose-400">
                  <AlertTriangle className="w-5 h-5 shrink-0" />
                  <h3 className="text-sm font-bold">Failed to complete intelligence inquiry</h3>
                </div>
                <p className="text-xs text-slate-300">{turn.error}</p>
              </div>
            ) : turn.response ? (
              <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-indigo-500/30 bg-slate-900/40 shadow-2xl space-y-6">
                {/* Header / City Tag & Telemetry */}
                <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {turn.response.city_name || turn.response.city_id}
                    </span>
                    {turn.response.country && (
                      <span className="text-xs text-slate-400">{turn.response.country}</span>
                    )}
                  </div>

                  {/* Groq LLM Telemetry Pill */}
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-[11px] text-slate-400 bg-slate-950/80 px-3 py-1.5 rounded-full border border-slate-800">
                    <span className="flex items-center gap-1 font-mono text-indigo-300">
                      <Cpu className="w-3 h-3 text-indigo-400" />
                      {turn.response.llm.model}
                    </span>
                    <span className="flex items-center gap-1 text-slate-500 border-l border-slate-800 pl-2">
                      <Clock className="w-3 h-3" />
                      {Math.round(turn.response.llm.latency_ms)}ms
                    </span>
                    <span className="flex items-center gap-1 text-emerald-400 border-l border-slate-800 pl-2">
                      <CheckCircle2 className="w-3 h-3" />
                      {Math.round(turn.response.confidence * 100)}% Confidence
                    </span>
                  </div>
                </div>

                {/* Grounded Answer Text */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Grounded Multi-Agent Assessment
                    </h3>
                    <button
                      type="button"
                      onClick={() => handleCopyAnswer(turn.id, turn.response!.answer)}
                      className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-white px-2 py-1 rounded bg-slate-900 border border-slate-800 transition-colors"
                      title="Copy answer text"
                    >
                      {copiedTurnId === turn.id ? (
                        <>
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span className="text-emerald-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Answer</span>
                        </>
                      )}
                    </button>
                  </div>
                  <div className="text-slate-100 text-sm sm:text-base leading-relaxed whitespace-pre-line font-normal">
                    {turn.response.answer}
                  </div>
                </div>

                {/* Recommendation Highlight */}
                {turn.response.recommendation && (
                  <div className="p-4 rounded-2xl bg-gradient-to-r from-emerald-950/40 to-indigo-950/40 border border-emerald-500/30 flex items-start gap-3">
                    <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 shrink-0">
                      <Lightbulb className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">
                        Recommendation & Actionable Insight
                      </h4>
                      <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                        {turn.response.recommendation}
                      </p>
                    </div>
                  </div>
                )}

                {/* Key Points */}
                {turn.response.key_points && turn.response.key_points.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Key Takeaways
                    </h4>
                    <ul className="space-y-2">
                      {turn.response.key_points.map((pt, idx) => (
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
                {turn.response.warnings && turn.response.warnings.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                    <div>
                      <strong>Data Limitations & Warnings:</strong>
                      <ul className="list-disc list-inside mt-1 space-y-0.5 text-amber-200">
                        {turn.response.warnings.map((w, wIdx) => (
                          <li key={wIdx}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Sources list */}
                {turn.response.sources && turn.response.sources.length > 0 && (
                  <div className="pt-4 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                      <Database className="w-3.5 h-3.5 text-indigo-400" />
                      <span>Grounded Data Sources:</span>
                    </span>
                    {turn.response.sources.map((src, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded text-[11px] bg-slate-900 border border-slate-800 text-slate-300"
                      >
                        {src}
                      </span>
                    ))}
                  </div>
                )}

                {/* Evidence Chunks Used */}
                {turn.response.evidence_used && turn.response.evidence_used.length > 0 && (
                  <div className="space-y-3 pt-2">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-indigo-400" />
                      <h4 className="text-sm font-bold text-white">
                        Retrieved Evidence Chunks ({turn.response.evidence_used.length})
                      </h4>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {turn.response.evidence_used.map((ev, idx) => (
                        <EvidenceCard key={idx} evidence={ev} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Quick Follow-up Suggestions */}
                <div className="pt-4 border-t border-slate-800/80 space-y-2">
                  <span className="text-[11px] font-semibold text-slate-500 block">
                    Suggested Follow-Up Inquiries for this city:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {FOLLOWUP_PROMPTS.map((prompt, pIdx) => (
                      <button
                        key={pIdx}
                        type="button"
                        onClick={() => handleExecuteQuery(prompt, turn.cityId)}
                        className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-indigo-300 text-xs flex items-center gap-1 transition-colors"
                      >
                        <span>{prompt}</span>
                        <ArrowRight className="w-3 h-3 text-indigo-400" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : null}
          </article>
        ))}

        <div ref={threadBottomRef} />
      </div>
    </div>
  );
};
