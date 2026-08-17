import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Play, 
  ShieldCheck, 
  Cpu, 
  Activity, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Layers,
  Sparkles
} from 'lucide-react';

export const HeroCommandStage: React.FC = () => {
  return (
    <section className="relative pt-12 pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col items-center text-center z-10">
      
      {/* Overhead Cinematic Spotlight and Lighting Cone */}
      <div className="cinematic-spotlight" />
      <div className="cinematic-beam" />

      {/* Pill Badge */}
      <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-400/25 text-blue-400 text-xs font-semibold tracking-wider uppercase mb-6 z-10 shadow-sm backdrop-blur-md">
        <Sparkles className="w-3.5 h-3.5 text-blue-400" />
        <span>Deterministic Executive Intelligence</span>
      </div>

      {/* Tagline Headline */}
      <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-5xl leading-[1.1] mb-5 z-10">
        Know What’s Happening.<br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-400">
          Understand Why.
        </span><br />
        Decide What Comes Next.
      </h1>

      {/* High-Impact Executive Statement */}
      <p className="text-lg sm:text-2xl font-medium text-gray-200 max-w-3xl mb-4 z-10">
        Most platforms tell you what happened.<br className="hidden sm:inline" />
        <span className="text-blue-300 font-semibold"> DecisionOS determines why it happened and calculates what to do next.</span>
      </p>

      {/* Description Subtext */}
      <p className="text-sm sm:text-base text-gray-400 max-w-2xl mb-8 leading-relaxed z-10">
        DecisionOS transforms business telemetry into explainable intelligence through deterministic KPI evaluation, causal root-cause discovery, and prioritized executive interventions — powered by DEX.
      </p>

      {/* Primary CTAs */}
      <div className="flex flex-wrap items-center justify-center gap-4 mb-16 z-10">
        <Link to="/dashboard" className="btn-primary-command">
          <span>Launch Command Center</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
        <a href="#pipeline" className="btn-secondary-command">
          <Play className="w-4 h-4 text-blue-400 fill-blue-400/30" />
          <span>Explore Decision Flow</span>
        </a>
      </div>

      {/* ======================================================================
          Command Center Stage: DEX at Center + 4 Structured Telemetry Pods
          ====================================================================== */}
      <div className="pedestal-stage w-full">
        
        <div className="command-center-stage-grid">
          
          {/* 1. Top-Left Pod: Business Health */}
          <div className="pod-top-left glass-panel p-4 text-left border-white/10 hover:border-emerald-500/40 transition-all">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1 font-medium">
              <span>Business Health</span>
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold text-white tracking-tight">84</span>
              <span className="text-xs text-gray-400">/ 100</span>
            </div>
            <div className="mt-2 text-[11px] text-emerald-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Good Execution Status</span>
            </div>
          </div>

          {/* 2. Top-Right Pod: Forecast Confidence */}
          <div className="pod-top-right glass-panel p-4 text-left border-white/10 hover:border-blue-500/40 transition-all">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1 font-medium">
              <span>Forecast Confidence</span>
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold text-white tracking-tight">94%</span>
            </div>
            <div className="mt-2 text-[11px] text-blue-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
              <span>High Stability Index</span>
            </div>
          </div>

          {/* 3. Central Epistemic Pod: DEX Intelligence Core */}
          <div className="pod-center-dex">
            <div className="dex-core-card">
              <div className="dex-avatar-halo">
                <Cpu className="w-9 h-9 text-blue-400" />
              </div>
              <div className="text-xs font-semibold tracking-widest text-blue-400 uppercase mb-0.5">
                Intelligence Core
              </div>
              <div className="text-lg font-bold text-white tracking-tight">
                DEX
              </div>
              <div className="text-xs text-gray-300 font-medium mt-1">
                Executive Intelligence Partner
              </div>
              <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-center gap-2 text-[11px] text-emerald-400 font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Deterministic DAG Active</span>
              </div>
            </div>
          </div>

          {/* 4. Bottom-Left Pod: Top Operational Risk */}
          <div className="pod-bottom-left glass-panel p-4 text-left border-white/10 hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1 font-medium">
              <span>Top Operational Risk</span>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <div className="text-sm font-bold text-white truncate">
              Retention Drag
            </div>
            <div className="mt-2 text-[11px] text-amber-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <span>High Revenue Exposure</span>
            </div>
          </div>

          {/* 5. Bottom-Right Pod: Recommended Executive Action */}
          <div className="pod-bottom-right glass-panel p-4 text-left border-white/10 hover:border-cyan-500/40 transition-all">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1 font-medium">
              <span>Recommended Action</span>
              <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
            </div>
            <div className="text-sm font-bold text-white truncate">
              Reallocation Plan
            </div>
            <div className="mt-2 text-[11px] text-cyan-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              <span>P1 Critical Intervention</span>
            </div>
          </div>

        </div>

        {/* 3D Luminescent Pedestal Stage */}
        <div className="stage-pedestal-platform hidden sm:block">
          <div className="pedestal-top" />
          <div className="pedestal-ring-glow" />
        </div>

      </div>

      {/* Trust & Precision Bar */}
      <div className="mt-12 pt-8 border-t border-white/10 w-full max-w-4xl flex flex-wrap items-center justify-around gap-6 text-xs text-gray-400 font-medium">
        <div className="flex items-center gap-2">
          <span className="text-blue-400 font-bold">✓</span>
          <span>100% Deterministic Calculations</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold">✓</span>
          <span>Causal Root Cause DAG</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-purple-400 font-bold">✓</span>
          <span>SHA-256 State Replay</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-cyan-400 font-bold">✓</span>
          <span>783+ Automated Tests</span>
        </div>
      </div>

    </section>
  );
};
