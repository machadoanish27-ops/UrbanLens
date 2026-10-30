import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { URBAN_REPORTS } from '../data/urbanData';
import type { UrbanReport } from '../data/urbanData';
import { FileText, Download, Share2, Eye } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const { currentCity } = useUrban();
  const [selectedReport, setSelectedReport] = useState<UrbanReport | null>(null);

  const handleExport = (rep: UrbanReport) => {
    alert(`Exporting "${rep.title}" as PDF telemetry dossier...`);
  };

  const handleShare = (rep: UrbanReport) => {
    navigator.clipboard?.writeText(window.location.href);
    alert(`Encrypted share token generated for "${rep.title}". Link copied.`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>EXECUTIVE AUDITS & DOSSIERS</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            {currentCity.name} Intelligence Reports
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Synthesized operational papers covering vehicular throughput audits, coastal particulate vectors, and higher education indices.
          </p>
        </div>
      </div>

      {/* Reports Grid (Section 25) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {URBAN_REPORTS.map((rep) => (
          <div
            key={rep.id}
            className="rounded-2xl bg-[#0B1726] border border-[#1E334A] hover:border-cyan-500/50 p-6 transition-all duration-200 shadow-xl flex flex-col justify-between space-y-5"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-cyan-400">{rep.date}</span>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-500/40 font-bold">
                  {rep.status}
                </span>
              </div>

              <h2 className="text-base font-bold font-mono text-white leading-snug">
                {rep.title}
              </h2>

              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                {rep.summary}
              </p>

              <div className="p-3 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs">
                <span className="text-[10px] font-mono text-slate-400 uppercase font-semibold">KEY FINDING:</span>
                <p className="text-cyan-300 font-sans mt-0.5 text-xs font-medium">
                  {rep.keyFinding}
                </p>
              </div>

              <div className="text-[10px] font-mono text-slate-400 pt-1">
                Author: {rep.author} · {rep.pages} Pages
              </div>
            </div>

            {/* Action Buttons: View, Export, Share */}
            <div className="grid grid-cols-3 gap-2 pt-3 border-t border-[#1E334A]">
              <button
                onClick={() => setSelectedReport(rep)}
                className="py-2 rounded-lg bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-200 transition-colors flex items-center justify-center gap-1"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>View</span>
              </button>
              <button
                onClick={() => handleExport(rep)}
                className="py-2 rounded-lg bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-200 transition-colors flex items-center justify-center gap-1"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export</span>
              </button>
              <button
                onClick={() => handleShare(rep)}
                className="py-2 rounded-lg bg-[#07111F] border border-[#1E334A] hover:border-cyan-500/40 text-xs font-mono text-slate-200 transition-colors flex items-center justify-center gap-1"
              >
                <Share2 className="w-3.5 h-3.5" />
                <span>Share</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Report Modal Viewer */}
      {selectedReport && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in"
          onClick={() => setSelectedReport(null)}
        >
          <div
            className="w-full max-w-2xl bg-[#0B1726] border border-cyan-500/40 rounded-2xl p-6 shadow-2xl space-y-4 animate-in zoom-in-95"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
              <span className="text-xs font-mono text-cyan-400">{selectedReport.date} · DOSSIER #{selectedReport.id}</span>
              <button onClick={() => setSelectedReport(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>
            <h2 className="text-xl font-bold font-mono text-white">{selectedReport.title}</h2>
            <p className="text-xs text-slate-300 leading-relaxed">{selectedReport.summary}</p>
            <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] text-xs font-mono space-y-2">
              <div className="text-cyan-300 font-bold">OPERATIONAL SYNTHESIS:</div>
              <p className="text-slate-200">{selectedReport.keyFinding}</p>
            </div>
            <div className="flex justify-end gap-3 pt-3">
              <button onClick={() => setSelectedReport(null)} className="px-4 py-2 text-xs font-mono text-slate-400 hover:text-white">Close</button>
              <button onClick={() => handleExport(selectedReport)} className="px-4 py-2 rounded-xl bg-cyan-500 text-slate-950 font-bold font-mono text-xs">Download PDF</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
