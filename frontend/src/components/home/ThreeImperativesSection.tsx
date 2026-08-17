import React, { useState } from 'react';
import { 
  Eye, 
  HelpCircle, 
  CheckSquare, 
  Activity, 
  GitBranch, 
  TrendingUp, 
  ShieldCheck, 
  ArrowUpRight,
  Sparkles
} from 'lucide-react';

export const ThreeImperativesSection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'know' | 'why' | 'decide'>('know');

  return (
    <section id="imperatives" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 relative">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
          Executive Decision Lifecycle
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Three Executive Imperatives
        </h2>
        <p className="mt-3 text-base sm:text-lg text-gray-400">
          The three non-negotiable questions every business leader must answer with empirical confidence.
        </p>
      </div>

      {/* Tab Selectors */}
      <div className="flex justify-center mb-12">
        <div className="inline-flex p-1.5 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl">
          
          <button
            onClick={() => setActiveTab('know')}
            className={`flex items-center gap-2.5 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'know' 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Eye className="w-4 h-4" />
            <span>1. Know What's Happening</span>
          </button>

          <button
            onClick={() => setActiveTab('why')}
            className={`flex items-center gap-2.5 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'why' 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <HelpCircle className="w-4 h-4" />
            <span>2. Understand Why</span>
          </button>

          <button
            onClick={() => setActiveTab('decide')}
            className={`flex items-center gap-2.5 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              activeTab === 'decide' 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <CheckSquare className="w-4 h-4" />
            <span>3. Decide What Comes Next</span>
          </button>

        </div>
      </div>

      {/* Tab Panels */}
      <div className="glass-panel-elevated p-8 sm:p-10 border-white/10">
        
        {activeTab === 'know' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">
                Imperative 01
              </div>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-white mb-4">
                Continuous Operational & Strategic Telemetry
              </h3>
              <p className="text-gray-300 leading-relaxed mb-6">
                DecisionOS continuously monitors multi-tenant business KPIs, milestone velocity, and stage-gate governance adherence. It eliminates blind spots across revenue, margins, and operational capacity.
              </p>
              <div className="space-y-3 text-sm text-gray-300">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-400" />
                  <span>Real-Time Business Health Index (Normalized 0–100 scale)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>Deterministic Execution Velocity & Schedule Adherence</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span>Stage-Gate Governance & Compliance Score Tracking</span>
                </div>
              </div>
            </div>

            {/* Mock Telemetry Card */}
            <div className="p-6 rounded-xl bg-black/60 border border-white/10 font-mono text-xs text-gray-300 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <span className="text-blue-400 font-bold">TELEMETRY_MONITOR_ACTIVE</span>
                <span className="text-emerald-400 text-[10px] uppercase">STATUS: SYNCED</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="text-[10px] text-gray-400 uppercase">Gross Margin</div>
                  <div className="text-lg font-bold text-white mt-1">68.4% <span className="text-[11px] text-red-400">(-3.1%)</span></div>
                </div>
                <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                  <div className="text-[10px] text-gray-400 uppercase">Milestone Velocity</div>
                  <div className="text-lg font-bold text-white mt-1">88.5% <span className="text-[11px] text-emerald-400">(+4.2%)</span></div>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-300 text-[11px]">
                Summary: Revenue trajectory stable, operational fulfillment latency elevated (+2.4 days above benchmark).
              </div>
            </div>
          </div>
        )}

        {activeTab === 'why' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">
                Imperative 02
              </div>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-white mb-4">
                Causal Root Cause Analysis (DAG Graph)
              </h3>
              <p className="text-gray-300 leading-relaxed mb-6">
                When performance deteriorates, DecisionOS traverses causal directed acyclic graphs (DAGs) to isolate upstream root causes from downstream symptom findings.
              </p>
              <div className="space-y-3 text-sm text-gray-300">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>Separates Primary Root Causes from Symptomatic Findings</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-amber-400" />
                  <span>Quantifies Upstream vs. Downstream Financial Impact</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-purple-400" />
                  <span>Pareto Loss Decomposition & Single Point of Failure Discovery</span>
                </div>
              </div>
            </div>

            {/* Mock Causal Graph Card */}
            <div className="p-6 rounded-xl bg-black/60 border border-white/10 font-mono text-xs text-gray-300 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <span className="text-emerald-400 font-bold">CAUSAL_DAG_TRAVERSAL</span>
                <span className="text-cyan-400 text-[10px]">CONFIDENCE: 96.2%</span>
              </div>
              <div className="space-y-2 text-[11px]">
                <div className="p-2.5 rounded bg-red-500/10 border border-red-500/25 text-red-300 flex items-center justify-between">
                  <span>[ROOT CAUSE] ERP Database Sync Latency</span>
                  <span className="text-[10px] text-red-400">Impact: 78.4%</span>
                </div>
                <div className="pl-4 text-gray-500 text-[10px]">↓ triggers</div>
                <div className="p-2.5 rounded bg-amber-500/10 border border-amber-500/25 text-amber-300 flex items-center justify-between">
                  <span>[INTERMEDIATE] Warehouse Dispatch Delay (+3.8d)</span>
                  <span className="text-[10px] text-amber-400">Impact: 62.1%</span>
                </div>
                <div className="pl-4 text-gray-500 text-[10px]">↓ triggers</div>
                <div className="p-2.5 rounded bg-white/5 border border-white/10 text-gray-300 flex items-center justify-between">
                  <span>[SYMPTOM] Customer Churn Spike (-14.2%)</span>
                  <span className="text-[10px] text-gray-400">Impact: Surface</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'decide' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">
                Imperative 03
              </div>
              <h3 className="text-2xl sm:text-3xl font-extrabold text-white mb-4">
                Prioritized Intervention Queues & 100% Explainability
              </h3>
              <p className="text-gray-300 leading-relaxed mb-6">
                DecisionOS generates prioritized executive actions with 100% mathematical driver attribution. Every recommended intervention is ranked by expected value, risk-discounted ROI, and portfolio capacity.
              </p>
              <div className="space-y-3 text-sm text-gray-300">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span>5-Tier Intervention Queue (Critical $\to$ Stabilization $\to$ Acceleration)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-400" />
                  <span>Risk-Discounted ROI Prioritization & Capital Allocation</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span>100% Mathematical Driver Breakdown (Zero AI Hallucination)</span>
                </div>
              </div>
            </div>

            {/* Mock Decision Queue Card */}
            <div className="p-6 rounded-xl bg-black/60 border border-white/10 font-mono text-xs text-gray-300 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-white/10 pb-3">
                <span className="text-cyan-400 font-bold">EXECUTIVE_INTERVENTION_QUEUE</span>
                <span className="text-emerald-400 text-[10px]">PRIORITY: P1_CRITICAL</span>
              </div>
              <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-400/30 text-blue-200">
                <div className="font-bold text-white text-xs mb-1">Fleet Logistics Realignment</div>
                <div className="text-[11px] text-gray-300">Decision Score: 84.5 • Expected Value: +$380,000</div>
              </div>
              <div className="space-y-1.5 text-[11px] text-gray-400 border-t border-white/5 pt-2">
                <div className="flex justify-between">
                  <span>Strategic Value Driver (25%):</span>
                  <span className="text-white">88.0</span>
                </div>
                <div className="flex justify-between">
                  <span>Execution Health Driver (20%):</span>
                  <span className="text-white">41.0</span>
                </div>
                <div className="flex justify-between">
                  <span>ROI Realization Driver (15%):</span>
                  <span className="text-white">37.0</span>
                </div>
                <div className="flex justify-between font-bold text-cyan-300 pt-1">
                  <span>Driver Attribution Coverage:</span>
                  <span>100.0%</span>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>

    </section>
  );
};
