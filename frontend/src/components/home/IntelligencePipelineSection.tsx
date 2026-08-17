import React, { useState } from 'react';
import { 
  Database, 
  BarChart2, 
  Search, 
  GitMerge, 
  Target, 
  ShieldAlert, 
  History, 
  Cpu, 
  ChevronRight,
  Code2
} from 'lucide-react';

interface PipelineStage {
  id: string;
  name: string;
  subtitle: string;
  icon: any;
  engine: string;
  description: string;
  formula: string;
  sampleOutput: string;
  color: string;
}

const PIPELINE_STAGES: PipelineStage[] = [
  {
    id: 'data',
    name: 'Business Data',
    subtitle: 'Collect & Ingest',
    icon: Database,
    engine: 'Dataset Ingestion & Validation Service',
    description: 'Ingests multi-tenant operational records (CSV, JSON, SQL) with schema inference, column classification, and completeness checks.',
    formula: 'Completeness = (ValidCells / TotalCells) * 100%',
    sampleOutput: '38,400 rows processed • Data Quality Index: 99.4%',
    color: '#a7c8ff'
  },
  {
    id: 'kpi',
    name: 'KPI Engine',
    subtitle: 'Measure Metrics',
    icon: BarChart2,
    engine: 'Deterministic KPI Analytics Engine',
    description: 'Computes multi-dimensional business health and execution health without stochastic AI models.',
    formula: 'HealthScore = Σ(w_i * NormalizedMetric_i) / Σ(w_i)',
    sampleOutput: 'Revenue Growth: -18.2% • Health Score: 41.0 (Critical)',
    color: '#38bdf8'
  },
  {
    id: 'diagnostics',
    name: 'Diagnostics',
    subtitle: 'Detect Findings',
    icon: Search,
    engine: 'Rule-Based Diagnostic Finding Engine',
    description: 'Evaluates domain business rules to detect operational bottlenecks, margin compression, and customer retention anomalies.',
    formula: 'FindingSeverity = f(MagnitudeDelta, HistoricalVariance)',
    sampleOutput: '3 Critical Findings: Carrier Dispatch Delay (+3.8d)',
    color: '#4ade80'
  },
  {
    id: 'causal',
    name: 'Root Causes',
    subtitle: 'Find What Matters',
    icon: GitMerge,
    engine: 'Causal Root Cause DAG Engine',
    description: 'Traverses directed acyclic causality graphs to isolate primary root causes from downstream symptom findings.',
    formula: 'RootCauseWeight = UpstreamReachability * DirectEffectSize',
    sampleOutput: 'Isolated Root Cause: Legacy ERP Inventory Sync Latency',
    color: '#facc15'
  },
  {
    id: 'recommendations',
    name: 'Recommendations',
    subtitle: 'Actionable Steps',
    icon: Target,
    engine: 'Strategic Recommendation Engine',
    description: 'Generates prioritized operational steps based on expected impact, implementation effort, and time to value.',
    formula: 'PriorityScore = (StrategicImpact * 0.6) + ((10 - Effort) * 0.4)',
    sampleOutput: 'Recommendation: Deploy Real-Time Warehouse Pods (P1)',
    color: '#fb923c'
  },
  {
    id: 'governance',
    name: 'Governance & ROI',
    subtitle: 'Track Benefits',
    icon: ShieldAlert,
    engine: 'Stage-Gate Governance & Benefits Engine',
    description: 'Monitors milestone velocity, stage-gate compliance, and expected vs. realized financial ROI.',
    formula: 'RealizationRate = (RealizedValue / ExpectedValue) * 100%',
    sampleOutput: 'Stage Gate: Stage 3 Approved • Projected ROI: 3.4x',
    color: '#f43f5e'
  },
  {
    id: 'snapshots',
    name: 'Historical Replay',
    subtitle: 'Lossless Audit',
    icon: History,
    engine: 'Cryptographic Snapshot Replay Engine',
    description: 'Maintains SHA-256 historical state ancestry for lossless point-in-time state reconstruction and longitudinal momentum analysis.',
    formula: 'Checksum = SHA256(Timestamp + DatasetID + MetricsVector)',
    sampleOutput: 'Replay Verified: Valid State Match (Δ = 0.000%)',
    color: '#c084fc'
  },
  {
    id: 'dex',
    name: 'DEX Core',
    subtitle: 'Executive Partner',
    icon: Cpu,
    engine: 'Executive Intelligence & Decision Support Engine',
    description: 'Synthesizes all 7 upstream stages into explainable executive decision drivers and prioritized intervention queues.',
    formula: 'DecisionScore = 0.25*Value + 0.20*Health + 0.20*Risk + 0.15*ROI + 0.10*Gov',
    sampleOutput: 'Executive Briefing Ready: 100% Decision Driver Coverage',
    color: '#60a5fa'
  },
];

export const IntelligencePipelineSection: React.FC = () => {
  const [activeStageId, setActiveStageId] = useState<string>('dex');
  const activeStage = PIPELINE_STAGES.find(s => s.id === activeStageId) || PIPELINE_STAGES[7];

  return (
    <section id="pipeline" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 relative">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
          Architecture & Data Flow
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          The Intelligence Pipeline
        </h2>
        <p className="mt-3 text-base sm:text-lg text-gray-400">
          A fully integrated deterministic engine turning raw telemetry into auditable executive decisions.
        </p>
      </div>

      {/* 8-Stage Interactive Track */}
      <div className="glass-panel p-6 sm:p-8 mb-8 border-white/10 bg-[#0c0e12]/80">
        
        <div className="pipeline-track pb-4">
          {PIPELINE_STAGES.map((stage, idx) => {
            const Icon = stage.icon;
            const isActive = stage.id === activeStageId;
            return (
              <React.Fragment key={stage.id}>
                <div 
                  onClick={() => setActiveStageId(stage.id)}
                  className={`pipeline-node ${isActive ? 'active' : ''}`}
                >
                  <div 
                    className="node-icon-box"
                    style={{
                      borderColor: isActive ? stage.color : undefined,
                      boxShadow: isActive ? `0 0 20px ${stage.color}40` : undefined,
                    }}
                  >
                    <Icon className="w-5 h-5" style={{ color: isActive ? stage.color : '#9ca3af' }} />
                  </div>
                  <span className={`text-xs font-bold ${isActive ? 'text-white' : 'text-gray-400'}`}>
                    {stage.name}
                  </span>
                  <span className="text-[10px] text-gray-500 hidden sm:inline">
                    {stage.subtitle}
                  </span>
                </div>

                {idx < PIPELINE_STAGES.length - 1 && (
                  <div className="node-connector-arrow hidden md:block">
                    <ChevronRight className="w-4 h-4 text-gray-600" />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Stage Inspector Box */}
        <div className="mt-6 pt-6 border-t border-white/10 grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3 mb-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase" style={{ backgroundColor: `${activeStage.color}20`, color: activeStage.color }}>
                Stage Engine
              </span>
              <span className="text-sm font-semibold text-white">
                {activeStage.engine}
              </span>
            </div>
            <p className="text-sm text-gray-300 leading-relaxed mt-2">
              {activeStage.description}
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs text-gray-400 font-mono">
              <Code2 className="w-4 h-4 text-blue-400" />
              <span className="text-gray-500">Algorithm:</span>
              <span className="text-blue-300 font-semibold">{activeStage.formula}</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-black/50 border border-white/10 flex flex-col justify-between">
            <div className="text-[11px] font-mono uppercase tracking-wider text-gray-400 mb-1 font-semibold">
              Live Engine Output
            </div>
            <div className="text-xs font-mono text-emerald-400 font-medium py-2">
              {activeStage.sampleOutput}
            </div>
            <div className="text-[10px] text-gray-500 font-mono flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>100% Deterministic Guarantee</span>
            </div>
          </div>

        </div>

      </div>

    </section>
  );
};
