import React from 'react';
import { BarChart3, LineChart, Cpu, ArrowRight, CheckCircle, XCircle } from 'lucide-react';

export const WhyDashboardsFailSection: React.FC = () => {
  return (
    <section id="why-decisionos" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 relative">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
          Strategic Differentiation
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Why Traditional Dashboards Fail
        </h2>
        <p className="mt-4 text-base sm:text-lg text-gray-400 leading-relaxed">
          Most dashboards tell you <span className="text-gray-200 font-semibold">what happened</span>.
          DecisionOS explains <span className="text-blue-400 font-semibold">why it happened</span> and calculates <span className="text-emerald-400 font-semibold">what to do next</span>.
        </p>
      </div>

      {/* 3 Comparison Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* 1. Traditional Dashboard */}
        <div className="glass-panel p-8 flex flex-col justify-between border-white/10 hover:border-red-500/30 transition-all bg-[#0d0e12]/60">
          <div>
            <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-6">
              <BarChart3 className="w-6 h-6 text-red-400" />
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-red-400 mb-1">
              Legacy Approach
            </div>
            <h3 className="text-xl font-bold text-white mb-3">
              Traditional Dashboard
            </h3>
            <p className="text-sm text-gray-400 leading-relaxed mb-6">
              Reports raw metrics and static graphs without causality. Requires executive teams to manually guess which anomalies matter.
            </p>
            <div className="space-y-2.5 text-xs text-gray-400 border-t border-white/5 pt-5">
              <div className="flex items-center gap-2 text-gray-300">
                <CheckCircle className="w-3.5 h-3.5 text-gray-500" />
                <span>Displays raw KPIs</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <XCircle className="w-3.5 h-3.5 text-red-400/80" />
                <span>Zero root cause analysis</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <XCircle className="w-3.5 h-3.5 text-red-400/80" />
                <span>No decision recommendations</span>
              </div>
            </div>
          </div>
          <div className="mt-8 p-3 rounded-lg bg-red-500/5 border border-red-500/15 text-xs text-red-300 font-mono">
            Output: "Revenue declined 18%."
          </div>
        </div>

        {/* 2. BI Platform */}
        <div className="glass-panel p-8 flex flex-col justify-between border-white/10 hover:border-amber-500/30 transition-all bg-[#0d0e12]/60">
          <div>
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mb-6">
              <LineChart className="w-6 h-6 text-amber-400" />
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-1">
              Intermediate Analytics
            </div>
            <h3 className="text-xl font-bold text-white mb-3">
              BI Platform
            </h3>
            <p className="text-sm text-gray-400 leading-relaxed mb-6">
              Aggregates historical trends and filters. Shows that performance changed across dimensions, but cannot trace parent-child mechanisms.
            </p>
            <div className="space-y-2.5 text-xs text-gray-400 border-t border-white/5 pt-5">
              <div className="flex items-center gap-2 text-gray-300">
                <CheckCircle className="w-3.5 h-3.5 text-gray-500" />
                <span>Reports historical trends</span>
              </div>
              <div className="flex items-center gap-2 text-gray-300">
                <CheckCircle className="w-3.5 h-3.5 text-gray-500" />
                <span>Multidimensional slice & dice</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <XCircle className="w-3.5 h-3.5 text-amber-400/80" />
                <span>No automated decision support</span>
              </div>
            </div>
          </div>
          <div className="mt-8 p-3 rounded-lg bg-amber-500/5 border border-amber-500/15 text-xs text-amber-300 font-mono">
            Output: "Trend shows 4-quarter decline."
          </div>
        </div>

        {/* 3. DecisionOS (The Solution) */}
        <div className="glass-panel-elevated p-8 flex flex-col justify-between border-blue-500/40 relative overflow-hidden shadow-2xl shadow-blue-500/10">
          <div className="absolute top-0 right-0 px-3 py-1 bg-gradient-to-r from-blue-600 to-emerald-500 text-white font-bold text-[10px] uppercase tracking-wider rounded-bl-lg">
            The Decision System
          </div>
          <div>
            <div className="w-12 h-12 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center mb-6 shadow-lg shadow-blue-500/25">
              <Cpu className="w-6 h-6 text-blue-400" />
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-blue-400 mb-1">
              Deterministic Intelligence
            </div>
            <h3 className="text-xl font-bold text-white mb-3">
              DecisionOS
            </h3>
            <p className="text-sm text-gray-300 leading-relaxed mb-6">
              Explains the root cause using causal graph propagation, scores executive actionability, and calculates deterministic intervention priorities.
            </p>
            <div className="space-y-2.5 text-xs text-gray-200 border-t border-white/10 pt-5">
              <div className="flex items-center gap-2 text-blue-300 font-medium">
                <CheckCircle className="w-3.5 h-3.5 text-blue-400" />
                <span>Know What’s Happening (Deterministic KPIs)</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-300 font-medium">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                <span>Understand Why (Causal DAG Root Causes)</span>
              </div>
              <div className="flex items-center gap-2 text-cyan-300 font-medium">
                <CheckCircle className="w-3.5 h-3.5 text-cyan-400" />
                <span>Decide What Next (Prioritized Interventions)</span>
              </div>
            </div>
          </div>
          <div className="mt-8 p-3 rounded-lg bg-blue-500/15 border border-blue-400/30 text-xs text-cyan-200 font-mono">
            Output: "Root Cause: ERP Sync Lag. Recommended: P1 Fleet Reallocation."
          </div>
        </div>

      </div>

    </section>
  );
};
