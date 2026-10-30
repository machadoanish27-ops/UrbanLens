/**
 * UrbanLens Core Engine & Pure Logic Computations
 * Handles PSO Swarm Mechanics, Quantum State Transformations, Metric Trends, and Data Trust Systems.
 */

export type DataTrustBadge =
  | 'VERIFIED'
  | 'LIVE'
  | 'PREDICTED'
  | 'INFERENCE'
  | 'SIMULATION'
  | 'DATA UNAVAILABLE';

export interface Particle {
  id: number;
  position: [number, number]; // [x, y] normalized 0..100
  velocity: [number, number];
  bestPosition: [number, number];
  fitness: number;
  bestFitness: number;
}

export interface PSOResult {
  particles: Particle[];
  globalBestPosition: [number, number];
  globalBestFitness: number;
  iteration: number;
  convergenceScore: number; // 0..100%
}

/**
 * Single step of 2D Particle Swarm Optimization for urban traffic/signal routing
 */
export function stepPSO(
  particles: Particle[],
  target: [number, number],
  w: number = 0.65, // inertia
  c1: number = 1.4, // cognitive (personal best)
  c2: number = 1.6  // social (global best)
): PSOResult {
  if (particles.length === 0) {
    return {
      particles: [],
      globalBestPosition: [50, 50],
      globalBestFitness: 0,
      iteration: 0,
      convergenceScore: 0,
    };
  }

  // Find current global best
  let gBestPos = [...particles[0].bestPosition] as [number, number];
  let gBestFitness = particles[0].bestFitness;

  for (const p of particles) {
    if (p.bestFitness > gBestFitness) {
      gBestFitness = p.bestFitness;
      gBestPos = [...p.bestPosition];
    }
  }

  const updatedParticles: Particle[] = particles.map((p) => {
    const r1 = Math.random();
    const r2 = Math.random();

    // Update velocity
    const vx = w * p.velocity[0] + c1 * r1 * (p.bestPosition[0] - p.position[0]) + c2 * r2 * (gBestPos[0] - p.position[0]);
    const vy = w * p.velocity[1] + c1 * r1 * (p.bestPosition[1] - p.position[1]) + c2 * r2 * (gBestPos[1] - p.position[1]);

    // Clamping velocity
    const maxV = 8.0;
    const clampedVx = Math.max(-maxV, Math.min(maxV, vx));
    const clampedVy = Math.max(-maxV, Math.min(maxV, vy));

    // Update position
    const newX = Math.max(5, Math.min(95, p.position[0] + clampedVx));
    const newY = Math.max(5, Math.min(95, p.position[1] + clampedVy));

    // Objective function: distance to target + signal synchrony bonus
    const distToTarget = Math.hypot(newX - target[0], newY - target[1]);
    const fitness = Math.max(0, 100 - distToTarget * 1.4);

    const isNewPersonalBest = fitness > p.bestFitness;
    const newBestPos: [number, number] = isNewPersonalBest ? [newX, newY] : [...p.bestPosition];
    const newBestFit = isNewPersonalBest ? fitness : p.bestFitness;

    return {
      id: p.id,
      position: [newX, newY],
      velocity: [clampedVx, clampedVy],
      bestPosition: newBestPos,
      fitness: Number(fitness.toFixed(2)),
      bestFitness: Number(newBestFit.toFixed(2)),
    };
  });

  // Recompute global best
  for (const p of updatedParticles) {
    if (p.bestFitness > gBestFitness) {
      gBestFitness = p.bestFitness;
      gBestPos = [...p.bestPosition];
    }
  }

  // Calculate average distance from swarm to gBest for convergence score
  const avgDist = updatedParticles.reduce((acc, p) => acc + Math.hypot(p.position[0] - gBestPos[0], p.position[1] - gBestPos[1]), 0) / updatedParticles.length;
  const convergenceScore = Math.max(0, Math.min(100, Math.round(100 - avgDist * 2)));

  return {
    particles: updatedParticles,
    globalBestPosition: gBestPos,
    globalBestFitness: Number(gBestFitness.toFixed(2)),
    iteration: 1,
    convergenceScore,
  };
}

/**
 * Metric Trend Calculator
 */
export function calculateMetricTrend(current: number, previous: number): {
  delta: number;
  percentage: number;
  direction: 'up' | 'down' | 'neutral';
  formatted: string;
} {
  const delta = current - previous;
  const percentage = previous === 0 ? 0 : (delta / previous) * 100;
  const direction = Math.abs(delta) < 0.001 ? 'neutral' : delta > 0 ? 'up' : 'down';
  const prefix = delta > 0 ? '+' : '';
  const formatted = `${prefix}${percentage.toFixed(1)}%`;

  return {
    delta: Number(delta.toFixed(2)),
    percentage: Number(percentage.toFixed(1)),
    direction,
    formatted,
  };
}

/**
 * Quantum State Amplitude Simulation
 */
export function simulateQuantumStateAmplitudes(qubits: number, theta: number): number[] {
  const statesCount = Math.min(16, Math.pow(2, qubits));
  const probabilities: number[] = [];
  let sum = 0;

  for (let i = 0; i < statesCount; i++) {
    // Generate simulated superposition distribution based on gate phase theta
    const raw = Math.pow(Math.cos(theta * (i + 1) * 0.4), 2) + 0.05 * Math.sin((i + 1) * 1.2);
    const prob = Math.max(0.01, raw);
    probabilities.push(prob);
    sum += prob;
  }

  return probabilities.map((p) => Number((p / sum).toFixed(4)));
}

/**
 * Evaluate Data Trust State
 */
export function evaluateDataTrust(
  hasData: boolean,
  isLiveStream: boolean,
  isModelInference: boolean,
  isSimulated: boolean
): DataTrustBadge {
  if (!hasData) return 'DATA UNAVAILABLE';
  if (isSimulated) return 'SIMULATION';
  if (isLiveStream) return 'LIVE';
  if (isModelInference) return 'INFERENCE';
  return 'VERIFIED';
}
