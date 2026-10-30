import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUrban } from '../../context/UrbanContext';
import { useCity, useAskIntelligence } from '../../hooks/useUrbanLens';
import {
  Sparkles,
  X,
  Send,
  ExternalLink,
  BookOpen
} from 'lucide-react';
import { DataTrustBadge } from './DataTrustBadge';

interface AiMessage {
  id: string;
  sender: 'user' | 'urbanlens';
  timestamp: string;
  text: string;
  sources?: string[];
  evidenceCount?: number;
  provider?: string;
  confidence?: number;
  latencyMs?: number;
}

export const AiDrawer: React.FC = () => {
  const { isAiModalOpen, toggleAiModal, activeCityId } = useUrban();
  const { data: cityResp } = useCity(activeCityId);
  const cityName = cityResp?.data?.name || 'Active City';

  const [inputText, setInputText] = useState('');
  const navigate = useNavigate();

  const askMutation = useAskIntelligence();

  const [conversation, setConversation] = useState<AiMessage[]>([
    {
      id: 'welcome-1',
      sender: 'urbanlens',
      timestamp: 'SYSTEM READY',
      text: `Hello! I am UrbanLens Intelligence. Ask me anything about ${cityName}'s climate, air quality, transit, universities, healthcare, cost of living, or relocation requirements. All responses are strictly grounded in verified database metrics and authoritative sources.`,
      provider: 'Groq Llama-3.3-70b + Multi-Agent Orchestrator',
      confidence: 0.98,
    },
  ]);

  if (!isAiModalOpen) return null;

  const handleSubmit = async (textToSubmit?: string) => {
    const query = (textToSubmit || inputText).trim();
    if (!query || askMutation.isPending) return;

    const userMsg: AiMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: query,
    };

    setConversation((prev) => [...prev, userMsg]);
    setInputText('');

    try {
      const resp = await askMutation.mutateAsync({
        query,
        city_id: activeCityId,
      });

      const data = resp.data;
      const aiMsg: AiMessage = {
        id: `ai-${Date.now()}`,
        sender: 'urbanlens',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: data.answer || 'No answer generated.',
        sources: data.sources || [],
        evidenceCount: data.evidence_used?.length || 0,
        provider: data.llm?.provider ? `${data.llm.provider} (${data.llm.model})` : 'UrbanLens Engine',
        confidence: 0.95,
        latencyMs: data.llm?.latency_ms,
      };

      setConversation((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: AiMessage = {
        id: `err-${Date.now()}`,
        sender: 'urbanlens',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `Unable to complete query: ${err?.message || 'Server error'}. Please check your connection or retry.`,
        provider: 'System Fallback',
      };
      setConversation((prev) => [...prev, errorMsg]);
    }
  };

  const presetQueries = [
    `How does public transit work in ${cityName}?`,
    `What is the cost of living and rent in ${cityName}?`,
    `What are the top universities in ${cityName}?`,
    `What is the climate and air quality like in ${cityName}?`,
  ];

  return (
    <div
      className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex justify-end animate-in fade-in duration-200"
      onClick={() => toggleAiModal(false)}
    >
      <div
        className="w-full max-w-lg bg-[#07111F] border-l border-[#1E334A] h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div className="h-16 px-5 border-b border-[#1E334A] flex items-center justify-between shrink-0 bg-[#0B1726]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-500 via-cyan-500 to-blue-500 p-[1px]">
              <div className="w-full h-full bg-[#030712] rounded-lg flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-cyan-400" />
              </div>
            </div>
            <div>
              <div className="text-sm font-bold font-mono text-white flex items-center gap-2">
                <span>AI INTELLIGENCE</span>
                <DataTrustBadge status="LIVE" size="sm" />
              </div>
              <div className="text-[10px] font-mono text-slate-400">
                Grounding: {cityName}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => {
                toggleAiModal(false);
                navigate('/app/ask');
              }}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E334A] transition-colors"
              title="Open Full AI Page"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
            <button
              onClick={() => toggleAiModal(false)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#1E334A] transition-colors"
              title="Close Drawer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Conversation Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
          {conversation.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[92%] rounded-2xl p-4 text-xs font-mono leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-cyan-950/70 border border-cyan-500/40 text-cyan-100 rounded-br-none'
                    : 'bg-[#0B1726] border border-[#1E334A] text-slate-200 rounded-bl-none shadow-lg'
                }`}
              >
                {/* Message Header */}
                <div className="flex items-center justify-between text-[10px] text-slate-400 mb-2 border-b border-[#1E334A]/50 pb-1">
                  <span className="font-bold text-cyan-400 uppercase">
                    {msg.sender === 'user' ? 'YOU' : 'URBANLENS AI'}
                  </span>
                  <span>{msg.timestamp}</span>
                </div>

                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* AI Metadata & Sources */}
                {msg.sender === 'urbanlens' && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-[#1E334A] space-y-1.5">
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                      <BookOpen className="w-3 h-3 text-cyan-400" />
                      <span>CITED EVIDENCE ({msg.sources.length} sources):</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {msg.sources.slice(0, 3).map((src, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded bg-[#07111F] border border-[#1E334A] text-[10px] text-slate-300 truncate max-w-[200px]"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {msg.provider && (
                  <div className="mt-2 text-[9px] text-slate-500 font-mono">
                    Provider: {msg.provider} {msg.latencyMs ? `(${Math.round(msg.latencyMs)}ms)` : ''}
                  </div>
                )}
              </div>
            </div>
          ))}

          {askMutation.isPending && (
            <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-[#0B1726] border border-[#1E334A] text-xs font-mono text-cyan-300 animate-pulse">
              <Sparkles className="w-4 h-4 animate-spin text-cyan-400" />
              <span>Consulting 7 domain agents & RAG knowledge corpus...</span>
            </div>
          )}
        </div>

        {/* Preset Suggestions */}
        <div className="p-3 bg-[#0B1726] border-t border-[#1E334A] space-y-1.5 shrink-0">
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
            Suggested Prompts for {cityName}:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {presetQueries.slice(0, 2).map((pq, idx) => (
              <button
                key={idx}
                onClick={() => handleSubmit(pq)}
                disabled={askMutation.isPending}
                className="px-2.5 py-1 rounded-lg bg-[#07111F] hover:bg-[#1E334A] border border-[#1E334A] text-[10px] font-mono text-slate-300 hover:text-cyan-300 transition-colors text-left truncate max-w-full"
              >
                {pq}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="p-3 bg-[#07111F] border-t border-[#1E334A] flex items-center gap-2 shrink-0"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={askMutation.isPending}
            placeholder={`Ask about ${cityName}...`}
            className="flex-1 px-3.5 py-2.5 rounded-xl bg-[#0B1726] border border-[#1E334A] focus:border-cyan-400 text-xs font-mono text-white placeholder-slate-500 outline-none"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || askMutation.isPending}
            className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-slate-950 font-bold transition-all shadow-[0_0_15px_rgba(34,211,238,0.2)]"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
