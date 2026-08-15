import React from 'react';
import {
  ArrowRight,
  ChevronRight,
  GitCommit,
  GitFork,
  HelpCircle,
  Link2,
  Sparkles,
  Zap,
} from 'lucide-react';
import { RootCauseItem } from '../../../types/dashboard';

interface RootCauseSectionProps {
  rootCauses: RootCauseItem[];
}

export const RootCauseSection: React.FC<RootCauseSectionProps> = ({ rootCauses }) => {
  const getStrengthColor = (strength: string) => {
    switch (strength.toUpperCase()) {
      case 'STRONG':
      case 'DEFINITIVE':
        return 'text-emerald-300 bg-emerald-500/20 border-emerald-500/30';
      case 'MODERATE':
        return 'text-cyan-300 bg-cyan-500/20 border-cyan-500/30';
      default:
        return 'text-slate-300 bg-slate-700/50 border-slate-600';
    }
  };

  const getNodeColor = (nodeType: string) => {
    switch (nodeType) {
      case 'ANOMALY':
        return 'border-rose-500/40 bg-rose-950/30 text-rose-300';
      case 'SYMPTOM':
        return 'border-amber-500/40 bg-amber-950/30 text-amber-300';
      case 'ROOT_CAUSE':
        return 'border-indigo-500/40 bg-indigo-950/30 text-indigo-300';
      case 'ACTION':
        return 'border-emerald-500/40 bg-emerald-950/30 text-emerald-300';
      default:
        return 'border-slate-700 bg-slate-900 text-slate-300';
    }
  };

  return (
    <section id="root_causes" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-amber-600 to-indigo-600 rounded-xl text-white shadow-lg">
            <GitFork className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Root Cause & Causal Chains
            </h2>
            <p className="text-xs text-slate-400">
              4-stage causal graphs mapping diagnostic anomalies to underlying operational bottlenecks and strategic remedies
            </p>
          </div>
        </div>
      </div>

      {/* Root Causes Grid */}
      {rootCauses.length === 0 ? (
        <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
          No causal relationships or root causes synthesized yet.
        </div>
      ) : (
        <div className="space-y-6">
          {rootCauses.map((rc) => (
            <div
              key={rc.root_cause_id}
              className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5"
            >
              {/* Header Info */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2.5 py-0.5 text-xs font-bold rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      Attribution: {Math.round(rc.attribution_percentage)}%
                    </span>
                    <span
                      className={`px-2.5 py-0.5 text-xs font-bold rounded-md border ${getStrengthColor(
                        rc.relationship_strength
                      )}`}
                    >
                      {rc.relationship_strength} Relationship
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-2">{rc.title}</h3>
                </div>

                <div className="text-xs text-slate-400 sm:text-right">
                  <div>Confidence: <strong className="text-slate-200">{Math.round(rc.confidence_score * 100)}%</strong></div>
                  <div>Impact Magnitude: <strong className="text-rose-400">{Math.round(rc.impact_score * 100)}%</strong></div>
                </div>
              </div>

              {/* Causal Explanation */}
              {rc.causal_explanation && (
                <p className="text-xs text-slate-300 bg-slate-950/50 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                  {rc.causal_explanation}
                </p>
              )}

              {/* 4-Stage Visual Causal Flow */}
              {rc.causal_chain && rc.causal_chain.length > 0 && (
                <div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-3">
                    Multi-Stage Causal Pathway
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {rc.causal_chain.map((step, idx) => (
                      <div key={idx} className="relative">
                        <div
                          className={`p-3 rounded-xl border h-full flex flex-col justify-between ${getNodeColor(
                            step.node_type
                          )}`}
                        >
                          <div>
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-[10px] font-black uppercase tracking-wider opacity-75">
                                Step 0{step.step_order} • {step.node_type.replace('_', ' ')}
                              </span>
                            </div>
                            <div className="text-xs font-bold mb-1">{step.title}</div>
                            <div className="text-[11px] opacity-90 leading-snug">
                              {step.description}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
