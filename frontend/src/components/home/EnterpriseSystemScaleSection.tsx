import React from 'react';
import { ShieldCheck, CheckCircle2, Cpu, Server, Database, Layers, GitBranch, Terminal } from 'lucide-react';

export const EnterpriseSystemScaleSection: React.FC = () => {
  const metrics = [
    {
      value: '783+',
      label: 'Automated Tests',
      sublabel: '100% Pass Rate (Unit, Integration & API)',
      icon: CheckCircle2,
      color: '#4edea3'
    },
    {
      value: '100+',
      label: 'REST API Endpoints',
      sublabel: 'High-Concurrency Asynchronous FastAPI',
      icon: Server,
      color: '#38bdf8'
    },
    {
      value: '25+',
      label: 'Intelligence Engines',
      sublabel: 'Deterministic Mathematical Analytics',
      icon: Cpu,
      color: '#a7c8ff'
    },
    {
      value: '40+',
      label: 'Domain Models',
      sublabel: 'SQLAlchemy 2.0 Normalized Schema',
      icon: Database,
      color: '#c084fc'
    },
    {
      value: '14',
      label: 'Completed Phases',
      sublabel: 'Phases 0 – 13 Architecture Verified',
      icon: Layers,
      color: '#fb923c'
    },
    {
      value: '100%',
      label: 'Deterministic Intelligence',
      sublabel: 'Zero Calculation Drift or AI Hallucination',
      icon: ShieldCheck,
      color: '#2e90ff'
    },
  ];

  return (
    <section id="scale" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 relative">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
          Enterprise Engineering & Scale
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Production Architecture Metrics
        </h2>
        <p className="mt-3 text-base sm:text-lg text-gray-400">
          Engineered with enterprise rigor, multi-tenant isolation, and complete deterministic auditability.
        </p>
      </div>

      {/* 6 Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {metrics.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="scale-metric-card flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center">
                    <Icon className="w-5 h-5" style={{ color: item.color }} />
                  </div>
                  <span className="text-[11px] font-mono uppercase tracking-wider text-gray-500 font-semibold">
                    Verified
                  </span>
                </div>
                <div className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-1 font-mono">
                  {item.value}
                </div>
                <div className="text-base font-bold text-gray-200 mb-1">
                  {item.label}
                </div>
              </div>
              <div className="text-xs text-gray-400 mt-2 pt-3 border-t border-white/5">
                {item.sublabel}
              </div>
            </div>
          );
        })}
      </div>

      {/* Tech Stack Pills */}
      <div className="p-6 rounded-2xl bg-black/40 border border-white/10 flex flex-wrap items-center justify-center gap-3 text-xs text-gray-300 font-medium">
        <span className="text-gray-500 uppercase tracking-wider font-mono mr-2 text-[11px]">Stack:</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">FastAPI</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">Python 3.10+</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">PostgreSQL 16</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">SQLAlchemy 2.0</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">Pydantic v2</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">React 19</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">TypeScript 5.x</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">Vite</span>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10">Pytest</span>
      </div>

    </section>
  );
};
