import React, { useState } from 'react';
import { useUrban } from '../context/UrbanContext';
import { QUANTUM_JOBS } from '../data/urbanData';
import type { QuantumJob } from '../data/urbanData';
import { simulateQuantumStateAmplitudes } from '../utils/engine';
import {
  Atom,
  Layers,
  Zap
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const QuantumQpuPage: React.FC = () => {
  const { currentCity } = useUrban();
  const [selectedJob, setSelectedJob] = useState<QuantumJob>(QUANTUM_JOBS[0]);
  const qubitsCount = 3; // 3 qubits = 8 states
  const gatePhase = 1.2;

  const amplitudes = simulateQuantumStateAmplitudes(qubitsCount, gatePhase);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-purple-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Atom className="w-4 h-4 text-purple-400 animate-spin" style={{ animationDuration: '8s' }} />
            <span>CRYO-QUANTUM PROCESSOR</span>
            <span>·</span>
            <DataTrustBadge status="SIMULATION" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            QUANTUM URBAN COMPUTE (QPU)
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            127-Qubit superconducting transmon quantum processor solving combinatorial city-scale route scheduling, fleet charging, and district micro-grid annealing for {currentCity.name}.
          </p>
        </div>

        {/* Cryo-Chamber Status Strip */}
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-[#07111F] border border-purple-500/30 text-right">
            <div className="text-[10px] font-mono text-slate-400">TEMPERATURE</div>
            <div className="text-sm font-bold font-mono text-purple-400">12.8 mK</div>
          </div>
          <div className="p-3 rounded-xl bg-[#07111F] border border-cyan-500/30 text-right">
            <div className="text-[10px] font-mono text-slate-400">COHERENCE T1 / T2</div>
            <div className="text-sm font-bold font-mono text-cyan-400">184 µs / 142 µs</div>
          </div>
        </div>
      </div>

      {/* Hardware Core Banner Image */}
      <div className="relative rounded-2xl overflow-hidden border border-purple-500/30 shadow-2xl h-48 md:h-64">
        <img
          src="/src/assets/images/quantum_compute_core_1793341280564.jpg"
          alt="Quantum Cryogenic Dilution Refrigerator"
          className="w-full h-full object-cover filter brightness-85"
          referrerPolicy="no-referrer"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#030712] via-[#030712]/50 to-transparent" />

        <div className="absolute bottom-4 left-6 right-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
          <div>
            <div className="text-base font-bold text-white uppercase flex items-center gap-2">
              <span>DR-7 ALPHA SUPERCONDUCTING LATTICE</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-500/40">ONLINE</span>
            </div>
            <div className="text-[11px] text-slate-300 mt-0.5">
              Zero-Noise Extrapolation (ZNE) active · Waveguide bus synchronized
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] text-slate-400">GLOBAL QUEUE: 3 JOBS</span>
            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
          </div>
        </div>
      </div>

      {/* Grid: Quantum Circuit Explorer (Left 7 Cols) + Job Queue (Right 5 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Circuit Explorer & State Probabilities */}
        <div className="lg:col-span-7 rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                PARAMETRIC QUANTUM CIRCUIT EXPLORER (QAOA)
              </h2>
            </div>
            <span className="text-[10px] font-mono text-slate-400">DEPTH: 180 GATES</span>
          </div>

          {/* Interactive Circuit Qubit Lines */}
          <div className="p-4 rounded-xl bg-[#07111F] border border-[#1E334A] space-y-4">
            <div className="text-[10px] font-mono text-slate-400 uppercase">
              QUBIT REGISTER & ENTANGLEMENT TOPOLOGY
            </div>

            {/* Qubit Wire 0 */}
            <div className="flex items-center gap-3 font-mono text-xs">
              <span className="w-8 text-cyan-400 font-bold">|q₀⟩</span>
              <div className="flex-1 h-0.5 bg-[#1E334A] relative flex items-center justify-around">
                <span className="px-2 py-1 rounded bg-purple-950 border border-purple-500/50 text-[10px] text-purple-300 font-bold z-10">H</span>
                <span className="px-2 py-1 rounded bg-blue-950 border border-blue-500/50 text-[10px] text-blue-300 font-bold z-10">RZ(θ)</span>
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 z-10" />
                <span className="px-2 py-1 rounded bg-slate-900 border border-slate-700 text-[10px] text-slate-300 z-10">M</span>
              </div>
            </div>

            {/* Qubit Wire 1 */}
            <div className="flex items-center gap-3 font-mono text-xs">
              <span className="w-8 text-cyan-400 font-bold">|q₁⟩</span>
              <div className="flex-1 h-0.5 bg-[#1E334A] relative flex items-center justify-around">
                <span className="px-2 py-1 rounded bg-purple-950 border border-purple-500/50 text-[10px] text-purple-300 font-bold z-10">H</span>
                <span className="px-2 py-1 rounded bg-blue-950 border border-blue-500/50 text-[10px] text-blue-300 font-bold z-10">RX(β)</span>
                <span className="px-1.5 py-0.5 rounded-full bg-cyan-950 border border-cyan-400 text-[9px] text-cyan-300 font-bold z-10">⊕</span>
                <span className="px-2 py-1 rounded bg-slate-900 border border-slate-700 text-[10px] text-slate-300 z-10">M</span>
              </div>
            </div>

            {/* Qubit Wire 2 */}
            <div className="flex items-center gap-3 font-mono text-xs">
              <span className="w-8 text-cyan-400 font-bold">|q₂⟩</span>
              <div className="flex-1 h-0.5 bg-[#1E334A] relative flex items-center justify-around">
                <span className="px-2 py-1 rounded bg-purple-950 border border-purple-500/50 text-[10px] text-purple-300 font-bold z-10">H</span>
                <span className="px-2 py-1 rounded bg-blue-950 border border-blue-500/50 text-[10px] text-blue-300 font-bold z-10">RZ(γ)</span>
                <span className="px-1.5 py-0.5 rounded-full bg-cyan-950 border border-cyan-400 text-[9px] text-cyan-300 font-bold z-10">⊕</span>
                <span className="px-2 py-1 rounded bg-slate-900 border border-slate-700 text-[10px] text-slate-300 z-10">M</span>
              </div>
            </div>
          </div>

          {/* Superposition Probability Histogram */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-slate-400">
              <span className="uppercase font-semibold">SUPERPOSITION EIGENSTATE DISTRIBUTION</span>
              <span>SUM: 1.000</span>
            </div>

            <div className="grid grid-cols-8 gap-1.5 h-28 items-end p-2.5 rounded-xl bg-[#07111F] border border-[#1E334A]">
              {amplitudes.map((prob, idx) => (
                <div key={idx} className="flex flex-col items-center gap-1 h-full justify-end group">
                  <div
                    className="w-full bg-gradient-to-t from-purple-600 to-cyan-400 rounded-t-sm transition-all duration-300 group-hover:brightness-125"
                    style={{ height: `${Math.max(6, prob * 100 * 2.8)}%` }}
                  />
                  <span className="text-[9px] font-mono text-slate-400">|{idx.toString(2).padStart(3, '0')}⟩</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Job Queue Panel */}
        <div className="lg:col-span-5 rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-[#1E334A] pb-3">
              <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
                QPU BATCH JOBS
              </h2>
              <span className="text-[10px] font-mono text-cyan-400">LIVE CRYO-QUEUE</span>
            </div>

            <div className="space-y-3">
              {QUANTUM_JOBS.map((job) => {
                const isSelected = selectedJob.id === job.id;
                const isCompleted = job.status === 'COMPLETED';
                const isExecuting = job.status === 'EXECUTING';

                return (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`p-4 rounded-xl cursor-pointer transition-all border ${
                      isSelected
                        ? 'bg-[#07111F] border-purple-500/50 shadow-md'
                        : 'bg-[#07111F]/50 border-[#1E334A] hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <span className="text-xs font-bold font-mono text-white">{job.id}</span>
                      <span
                        className={`text-[9px] font-mono px-2 py-0.5 rounded font-bold ${
                          isCompleted
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40'
                            : isExecuting
                            ? 'bg-purple-950 text-purple-300 border border-purple-500/40 animate-pulse'
                            : 'bg-slate-900 text-slate-400 border border-slate-700'
                        }`}
                      >
                        {job.status}
                      </span>
                    </div>

                    <p className="text-xs text-slate-200 font-sans font-medium line-clamp-1">
                      {job.title}
                    </p>

                    <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-[#1E334A] text-[10px] font-mono text-slate-400">
                      <div>QUBITS: <span className="text-white">{job.qubitsUsed}</span></div>
                      <div>SHOTS: <span className="text-white">{job.iterations}</span></div>
                      <div className="truncate text-right text-emerald-400">{job.energySavingPotential}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-[#1E334A] space-y-2">
            <button
              onClick={() => alert(`Submitted QPU Annealing circuit for ${currentCity.name}. Cryo-Job #QPU-${Math.floor(Math.random()*9000 + 1000)} queued.`)}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-mono font-bold text-xs tracking-wider transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)] flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4" />
              <span>SUBMIT ANNEALING JOB TO QPU</span>
            </button>
            <div className="text-center text-[10px] font-mono text-slate-500">
              SIMULATION MODE · SIMULATED RUNTIME 142.8 MS
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
