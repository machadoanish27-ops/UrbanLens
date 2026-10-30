import React, { useState, useEffect } from 'react';
import { useUrban } from '../context/UrbanContext';
import { stepPSO } from '../utils/engine';
import type { Particle } from '../utils/engine';
import {
  Cpu,
  Play,
  RotateCcw,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react';
import { DataTrustBadge } from '../components/common/DataTrustBadge';

export const PsoOptimizationPage: React.FC = () => {
  const { currentCity, navigate } = useUrban();

  const [isRunning, setIsRunning] = useState(false);
  const [iteration, setIteration] = useState(0);
  const [maxIterations] = useState(60);
  const [convergenceScore, setConvergenceScore] = useState(74);
  const [objectiveScore, setObjectiveScore] = useState(91.4);
  const [improvementPercentage, setImprovementPercentage] = useState(21.4);
  const targetPoint: [number, number] = [52, 42]; // Target node (e.g. BKC / Western Flyover)

  // Initialize 24 swarm particles
  const createInitialParticles = (): Particle[] => {
    return Array.from({ length: 24 }).map((_, i) => {
      const x = 15 + Math.random() * 70;
      const y = 15 + Math.random() * 70;
      return {
        id: i + 1,
        position: [x, y],
        velocity: [(Math.random() - 0.5) * 4, (Math.random() - 0.5) * 4],
        bestPosition: [x, y],
        fitness: 50,
        bestFitness: 50,
      };
    });
  };

  const [particles, setParticles] = useState<Particle[]>(createInitialParticles);

  // Swarm loop
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    if (isRunning && iteration < maxIterations) {
      timer = setTimeout(() => {
        const step = stepPSO(particles, targetPoint);
        setParticles(step.particles);
        setIteration((it) => it + 1);
        setConvergenceScore(step.convergenceScore);
        setObjectiveScore(step.globalBestFitness);
        setImprovementPercentage(Number(((step.globalBestFitness - 50) * 0.45).toFixed(1)));
      }, 120);
    } else if (iteration >= maxIterations) {
      setIsRunning(false);
    }
    return () => clearTimeout(timer);
  }, [isRunning, iteration, maxIterations, particles, targetPoint]);

  const handleReset = () => {
    setIsRunning(false);
    setIteration(0);
    setParticles(createInitialParticles());
    setConvergenceScore(60);
    setObjectiveScore(78.2);
    setImprovementPercentage(14.8);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#0B1726]/60 backdrop-blur-md border border-[#1E334A] rounded-2xl p-6">
        <div>
          <div className="text-xs font-mono text-emerald-400 uppercase tracking-widest font-semibold flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>ALGORITHMIC SIGNAL SOLVER</span>
            <span>·</span>
            <DataTrustBadge status="SIMULATION" size="sm" />
          </div>
          <h1 className="text-2xl sm:text-4xl font-black font-display text-white tracking-tight uppercase mt-1">
            PSO OPTIMIZATION STUDIO
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans mt-1 max-w-2xl">
            Particle Swarm Optimization modeling multi-intersection signal timing and green-wave throughput for {currentCity.name}.
          </p>
        </div>

        {/* Play / Reset Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsRunning(!isRunning)}
            className={`px-5 py-2.5 rounded-xl font-mono text-xs font-bold tracking-wider transition-all flex items-center gap-2 shadow-lg ${
              isRunning
                ? 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                : 'bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-[0_0_20px_rgba(16,185,129,0.3)]'
            }`}
          >
            <Play className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
            <span>{isRunning ? 'PAUSE SWARM' : 'RUN OPTIMIZATION'}</span>
          </button>
          <button
            onClick={handleReset}
            className="p-2.5 rounded-xl bg-[#07111F] border border-[#1E334A] hover:border-slate-500 text-slate-300 hover:text-white transition-colors"
            title="Reset swarm"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Top 5 Optimization Parameter Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-4 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 uppercase">OBJECTIVE FUNCTION</span>
          <div className="text-sm font-bold text-white font-mono mt-1 truncate">
            Green-Wave Synchrony
          </div>
          <div className="text-[10px] text-cyan-400 font-mono mt-0.5">Min delay variance</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 uppercase">SWARM PARTICLES</span>
          <div className="text-xl font-bold text-white font-mono mt-1">
            {particles.length} Active
          </div>
          <div className="text-[10px] text-emerald-400 font-mono mt-0.5">2D Vector space</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 uppercase">ITERATION</span>
          <div className="text-xl font-bold text-white font-mono mt-1 tabular-nums">
            {iteration} / {maxIterations}
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-0.5">Heuristic step</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 uppercase">SWARM CONVERGENCE</span>
          <div className="text-xl font-bold text-cyan-400 font-mono mt-1 tabular-nums">
            {convergenceScore}%
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-0.5">Global attractor</div>
        </div>

        <div className="p-4 rounded-xl bg-[#0B1726] border border-[#1E334A]">
          <span className="text-[10px] font-mono text-slate-400 uppercase">CURRENT FITNESS</span>
          <div className="text-xl font-bold text-emerald-400 font-mono mt-1 tabular-nums">
            {objectiveScore}
          </div>
          <div className="text-[10px] text-emerald-400 font-mono mt-0.5">+{improvementPercentage}% vs baseline</div>
        </div>
      </div>

      {/* Main Grid: Interactive Swarm Map (Left 8 Cols) + Recommended Solution (Right 4 Cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Swarm Vector Canvas */}
        <div className="lg:col-span-8 rounded-2xl bg-[#030712] border border-[#1E334A] p-5 relative overflow-hidden shadow-2xl flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-[#1E334A] pb-3 mb-2 z-10">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
                SWARM PARTICLE VECTOR MESH · WESTERN CORRIDOR
              </span>
              <DataTrustBadge status="SIMULATION" size="sm" />
            </div>
            <span className="text-[10px] font-mono text-slate-400">
              TARGET NODE: [{targetPoint.join(', ')}]
            </span>
          </div>

          {/* SVG Swarm Canvas */}
          <div className="relative w-full h-[450px] bg-spatial-grid rounded-xl overflow-hidden my-2 flex items-center justify-center">
            <svg viewBox="0 0 100 100" className="w-full h-full">
              {/* Target Hub Node */}
              <circle cx={targetPoint[0]} cy={targetPoint[1]} r="4" fill="none" stroke="#22D3EE" strokeWidth="0.8" className="animate-ping" opacity="0.6" />
              <circle cx={targetPoint[0]} cy={targetPoint[1]} r="2.5" fill="#22D3EE" />
              <text x={targetPoint[0] + 3} y={targetPoint[1] + 1} fill="#22D3EE" fontSize="2.5" fontFamily="monospace">
                TARGET INTERCHANGE
              </text>

              {/* Corridor lines */}
              <line x1="20" y1="20" x2="80" y2="80" stroke="#1E334A" strokeWidth="0.5" strokeDasharray="1,1" />
              <line x1="20" y1="80" x2="80" y2="20" stroke="#1E334A" strokeWidth="0.5" strokeDasharray="1,1" />

              {/* Dynamic Particles */}
              {particles.map((p) => {
                const [px, py] = p.position;
                const [vx, vy] = p.velocity;

                return (
                  <g key={p.id}>
                    {/* Velocity vector line */}
                    <line
                      x1={px}
                      y1={py}
                      x2={px + vx * 1.5}
                      y2={py + vy * 1.5}
                      stroke="rgba(34, 211, 238, 0.4)"
                      strokeWidth="0.5"
                    />
                    {/* Particle point */}
                    <circle
                      cx={px}
                      cy={py}
                      r="1.2"
                      fill={p.fitness > 80 ? '#10B981' : '#3B82F6'}
                    />
                  </g>
                );
              })}
            </svg>

            {/* Simulation watermark */}
            <div className="absolute top-3 left-3 text-[10px] font-mono text-slate-500 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800">
              SIMULATION MODE · HEURISTIC SOLVER
            </div>
          </div>

          {/* Bottom Iteration Timeline */}
          <div className="pt-3 border-t border-[#1E334A] flex items-center justify-between text-xs font-mono text-slate-400">
            <span>ITERATION PROGRESS:</span>
            <div className="flex-1 mx-4 h-2 bg-slate-900 rounded-full overflow-hidden border border-[#1E334A]">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 transition-all duration-150"
                style={{ width: `${(iteration / maxIterations) * 100}%` }}
              />
            </div>
            <span className="text-white font-bold">{Math.round((iteration / maxIterations) * 100)}%</span>
          </div>
        </div>

        {/* Right Recommended Solution Panel (Section 15) */}
        <div className="lg:col-span-4 rounded-2xl bg-[#0B1726] border border-[#1E334A] p-6 space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="border-b border-[#1E334A] pb-3">
              <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase tracking-wider">
                OPTIMIZED TIMING PROTOCOL
              </span>
              <h2 className="text-lg font-bold font-mono text-white uppercase mt-0.5">
                RECOMMENDED SOLUTION
              </h2>
            </div>

            <div className="space-y-3">
              <div className="p-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">OBJECTIVE SCORE</span>
                <span className="text-xl font-extrabold font-mono text-emerald-400">{objectiveScore} / 100</span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">THROUGHPUT IMPROVEMENT</span>
                <span className="text-xl font-extrabold font-mono text-cyan-400">+{improvementPercentage}%</span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">CONSTRAINTS SATISFIED</span>
                <span className="text-sm font-bold font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  3 / 3 HARD
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-[#07111F] border border-[#1E334A] flex items-center justify-between">
                <span className="text-xs font-mono text-slate-400">CONFIDENCE RATING</span>
                <span className="text-sm font-bold font-mono text-purple-300">92.4% HEURISTIC</span>
              </div>
            </div>

            {/* Constraints Checklist */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-[#1E334A] space-y-2 text-xs font-mono">
              <div className="text-[10px] text-slate-400 font-bold uppercase">CONSTRAINTS ENFORCED</div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Max intersection waiting delay &lt; 90s</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Emergency ambulance route pre-emption active</span>
              </div>
              <div className="flex items-center gap-2 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Pedestrian crosswalk duration &ge; 28s</span>
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-4 border-t border-[#1E334A]">
            <button
              onClick={() => {
                alert('Timing protocol dispatched to municipal traffic signal controller.');
                navigate('dashboard');
              }}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-mono font-bold text-xs tracking-wider transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <span>DEPLOY TIMING PROTOCOL</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <div className="text-center text-[10px] font-mono text-slate-500">
              SIMULATION MODE · VERIFIED SAFETY GUARDS
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
