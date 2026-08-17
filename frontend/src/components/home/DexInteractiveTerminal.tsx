import React, { useState } from 'react';
import { Cpu, Terminal, Play, CheckCircle, ShieldCheck, ArrowRight, CornerDownRight } from 'lucide-react';

interface Scenario {
  id: string;
  title: string;
  badge: string;
  inputTelemetry: string;
  rootCause: string;
  decisionScore: number;
  confidence: number;
  recommendation: string;
  priority: string;
  drivers: { name: string; weight: number; value: number }[];
}

const SCENARIOS: Scenario[] = [
  {
    id: 'supply-chain',
    title: 'Supply Chain Latency Spike',
    badge: 'Critical Escalation',
    inputTelemetry: 'Revenue ↓ 18% • Order Cancellations ↑ 22% • Carrier Dispatch Latency: +4.2d',
    rootCause: 'Legacy Warehouse ERP Inventory Synchronization Latency',
    decisionScore: 84.5,
    confidence: 95.0,
    recommendation: 'Reallocate 30% logistics capacity to regional fulfillment hubs.',
    priority: 'P1 - Critical Intervention',
    drivers: [
      { name: 'Strategic Value Driver', weight: 0.25, value: 88.0 },
      { name: 'Execution Health Drag', weight: 0.20, value: 41.0 },
      { name: 'Risk Attenuation Factor', weight: 0.20, value: 18.0 },
      { name: 'ROI Realization Potential', weight: 0.15, value: 75.0 },
      { name: 'Governance Compliance', weight: 0.10, value: 50.0 },
    ]
  },
  {
    id: 'customer-churn',
    title: 'Enterprise Customer Retention Drag',
    badge: 'Stabilization Priority',
    inputTelemetry: 'Renewal Rate ↓ 12.5% • Support Ticket Escalations ↑ 35% • SLA Breaches: 14',
    rootCause: 'Post-Migration Core Database Query Latency & Support Backlog',
    decisionScore: 78.2,
    confidence: 92.4,
    recommendation: 'Deploy dedicated VIP customer success pods and hotfix query cache.',
    priority: 'P2 - Immediate Action Required',
    drivers: [
      { name: 'Strategic Value Driver', weight: 0.25, value: 82.0 },
      { name: 'Execution Health Drag', weight: 0.20, value: 55.0 },
      { name: 'Risk Attenuation Factor', weight: 0.20, value: 30.0 },
      { name: 'ROI Realization Potential', weight: 0.15, value: 68.0 },
      { name: 'Governance Compliance', weight: 0.10, value: 70.0 },
    ]
  },
  {
    id: 'portfolio-investment',
    title: 'Portfolio Capital Allocation & ROI',
    badge: 'Investment Prioritization',
    inputTelemetry: 'Unallocated Budget: $650,000 • 6 Competing Modernization Initiatives',
    rootCause: 'Dispersed Capital Concentration Across Unaligned Initiatives',
    decisionScore: 89.0,
    confidence: 97.5,
    recommendation: 'Prioritize Edge Node Deployment (+3.8x ROI) and scale down low-yield initiatives.',
    priority: 'P1 - Strategic Investment',
    drivers: [
      { name: 'Strategic Value Driver', weight: 0.25, value: 92.0 },
      { name: 'Execution Health Drag', weight: 0.20, value: 86.0 },
      { name: 'Risk Attenuation Factor', weight: 0.20, value: 15.0 },
      { name: 'ROI Realization Potential', weight: 0.15, value: 94.0 },
      { name: 'Governance Compliance', weight: 0.10, value: 88.0 },
    ]
  }
];

export const DexInteractiveTerminal: React.FC = () => {
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('supply-chain');
  const activeScenario = SCENARIOS.find(s => s.id === selectedScenarioId) || SCENARIOS[0];

  return (
    <section id="dex-sandbox" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 relative">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
          Interactive Intelligence Simulator
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          DEX Scenario Sandbox
        </h2>
        <p className="mt-3 text-base sm:text-lg text-gray-400">
          Simulate real-world strategic anomalies and inspect DEX's deterministic reasoning chain in real time.
        </p>
      </div>

      {/* Main Sandbox Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        
        {/* Left Column: Scenario Selectors */}
        <div className="space-y-4">
          <div className="text-xs font-mono text-gray-400 uppercase tracking-wider font-semibold pl-1">
            Select Executive Scenario
          </div>

          {SCENARIOS.map(scenario => {
            const isSelected = scenario.id === selectedScenarioId;
            return (
              <button
                key={scenario.id}
                onClick={() => setSelectedScenarioId(scenario.id)}
                className={`w-full text-left p-5 rounded-xl border transition-all ${
                  isSelected 
                    ? 'bg-blue-600/15 border-blue-500/50 shadow-lg shadow-blue-500/10' 
                    : 'bg-[#0d0e12]/80 border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className={`px-2 py-0.5 rounded font-mono text-[10px] uppercase font-semibold ${
                    isSelected ? 'bg-blue-500/30 text-blue-300' : 'bg-white/5 text-gray-400'
                  }`}>
                    {scenario.badge}
                  </span>
                  <span className="text-[11px] font-mono text-gray-500">Score: {scenario.decisionScore}</span>
                </div>
                <div className={`text-sm font-bold ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                  {scenario.title}
                </div>
                <div className="text-xs text-gray-500 mt-2 truncate">
                  {scenario.inputTelemetry}
                </div>
              </button>
            );
          })}
        </div>

        {/* Right Column: Terminal Output (2 cols) */}
        <div className="lg:col-span-2 glass-panel-elevated p-6 sm:p-8 bg-[#090b0e] border-white/10 font-mono text-xs shadow-2xl">
          
          {/* Terminal Top Bar */}
          <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5 text-gray-400">
            <div className="flex items-center gap-2 text-blue-400 font-bold">
              <Terminal className="w-4 h-4" />
              <span>DEX_DECISION_ENGINE // ID: {activeScenario.id.toUpperCase()}</span>
            </div>
            <div className="flex items-center gap-2 text-[11px] text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>CONFIDENCE: {activeScenario.confidence}%</span>
            </div>
          </div>

          {/* 1. Input Telemetry */}
          <div className="mb-4 p-3 rounded-lg bg-black/50 border border-white/5">
            <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Raw Business Telemetry Ingested</div>
            <div className="text-gray-200">{activeScenario.inputTelemetry}</div>
          </div>

          {/* 2. Causal Root Cause */}
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300">
            <div className="text-[10px] text-red-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <CornerDownRight className="w-3 h-3" />
              <span>Causal DAG Root Cause Isolated</span>
            </div>
            <div className="font-semibold">{activeScenario.rootCause}</div>
          </div>

          {/* 3. Mathematical Decision Driver Decomposition */}
          <div className="mb-5 p-3 rounded-lg bg-black/50 border border-white/5 space-y-2">
            <div className="text-[10px] text-gray-500 uppercase tracking-wider flex justify-between">
              <span>Deterministic Factor Breakdown</span>
              <span className="text-blue-400">Driver Coverage: 100.0%</span>
            </div>
            {activeScenario.drivers.map((driver, idx) => (
              <div key={idx} className="flex justify-between items-center text-gray-400 text-[11px]">
                <span>{driver.name} ({(driver.weight * 100).toFixed(0)}% weight)</span>
                <span className="text-white font-bold">{driver.value.toFixed(1)} / 100</span>
              </div>
            ))}
          </div>

          {/* 4. DEX Action Recommendation */}
          <div className="p-4 rounded-xl bg-blue-600/15 border border-blue-500/40 text-blue-100">
            <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-cyan-300 mb-1">
              <span>Recommended Executive Action</span>
              <span className="px-2 py-0.5 rounded bg-blue-500/30 text-white text-[10px]">{activeScenario.priority}</span>
            </div>
            <div className="text-sm font-sans font-semibold text-white mt-1">
              {activeScenario.recommendation}
            </div>
            <div className="text-[10px] text-blue-300/80 mt-2 font-mono">
              Composite Decision Score: {activeScenario.decisionScore} • 100% Explainable
            </div>
          </div>

        </div>

      </div>

    </section>
  );
};
