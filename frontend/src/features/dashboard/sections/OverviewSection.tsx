import React from 'react';
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  Award,
  CheckCircle2,
  ChevronRight,
  Compass,
  DollarSign,
  Flame,
  LineChart,
  Minus,
  Percent,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';
import { OverviewPayload } from '../../../types/dashboard';

interface OverviewSectionProps {
  overview: OverviewPayload;
  onNavigateSection?: (sectionId: string) => void;
}

export const OverviewSection: React.FC<OverviewSectionProps> = ({
  overview,
  onNavigateSection,
}) => {
  const {
    health_dimensions,
    scorecard,
    statistics,
    top_risks,
    top_opportunities,
    active_alerts,
    watchlist_metrics,
    executive_summary_brief,
  } = overview;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 60) return 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10';
    if (score >= 40) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <section id="overview" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-indigo-600 rounded-xl text-white shadow-lg">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Executive Scorecard & Health</h2>
            <p className="text-xs text-slate-400">Synthesized holistic view of business health, operational risk, and value levers</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Health Gauge + Executive Scorecard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Overall Health Score Card */}
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-bl from-cyan-500/10 via-transparent to-transparent rounded-bl-full pointer-events-none" />
          <div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Business Health Index</span>
              <span className={`px-2.5 py-1 text-xs font-bold rounded-full border ${getScoreColor(health_dimensions.overall_score)}`}>
                {health_dimensions.status}
              </span>
            </div>

            <div className="mt-6 flex items-baseline gap-3">
              <span className="text-5xl font-black text-white tracking-tight">
                {health_dimensions.overall_score}
              </span>
              <span className="text-slate-500 text-lg font-medium">/ 100</span>
              {health_dimensions.delta !== 0 && (
                <span className={`inline-flex items-center text-xs font-bold ml-2 ${health_dimensions.delta > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {health_dimensions.delta > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                  {health_dimensions.delta > 0 ? `+${health_dimensions.delta}` : health_dimensions.delta} pts
                </span>
              )}
            </div>

            <p className="text-xs text-slate-400 mt-2">
              {executive_summary_brief || 'Aggregated multi-dimensional index based on operational diagnostics and performance targets.'}
            </p>
          </div>

          {/* Sub-Dimensions Bar Gauges */}
          <div className="mt-6 space-y-3 pt-4 border-t border-slate-800/80">
            <div className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-400">Financial Resilience</span>
                <span className="text-slate-200">{health_dimensions.financial_score}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full" style={{ width: `${health_dimensions.financial_score}%` }} />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-400">Operational Stability</span>
                <span className="text-slate-200">{health_dimensions.operational_score}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full" style={{ width: `${health_dimensions.operational_score}%` }} />
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-400">Customer Retention</span>
                <span className="text-slate-200">{health_dimensions.customer_score}%</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full" style={{ width: `${health_dimensions.customer_score}%` }} />
              </div>
            </div>
          </div>
        </div>

        {/* Executive Scorecard Metric Cards (4 cards in 2x2) */}
        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Revenue Health</span>
              <DollarSign className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-white">{scorecard.revenue_health_score}%</div>
              <div className="text-[11px] text-slate-400 mt-1">Direct pipeline & renewal predictability</div>
            </div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Operational Health</span>
              <Zap className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-white">{scorecard.operational_health_score}%</div>
              <div className="text-[11px] text-slate-400 mt-1">Efficiency, SLA targets, delivery friction</div>
            </div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Risk Exposure Index</span>
              <ShieldAlert className="w-4 h-4 text-rose-400" />
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-white">{scorecard.risk_exposure_score} / 100</div>
              <div className="text-[11px] text-slate-400 mt-1">Quantified business vulnerability exposure</div>
            </div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400">Forecast Confidence</span>
              <Award className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-4">
              <div className="text-2xl font-bold text-white">{Math.round(scorecard.forecast_confidence * 100)}%</div>
              <div className="text-[11px] text-slate-400 mt-1">Prophet statistical confidence interval</div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Risks & Top Opportunities (Side by Side) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Risks */}
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-rose-400" />
              <h3 className="text-sm font-bold text-white">Top Critical Risks</h3>
            </div>
            {onNavigateSection && (
              <button
                onClick={() => onNavigateSection('findings')}
                className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
              >
                View all <ChevronRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          {top_risks.length === 0 ? (
            <div className="text-xs text-slate-500 py-6 text-center">No high-severity risks identified.</div>
          ) : (
            <div className="space-y-3">
              {top_risks.slice(0, 3).map((r, idx) => (
                <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${getSeverityBadge(r.severity)}`}>
                        {r.severity}
                      </span>
                      <span className="text-xs font-semibold text-slate-200">{r.title}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">{r.impact}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Opportunities */}
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Top Value Creation Levers</h3>
            </div>
            {onNavigateSection && (
              <button
                onClick={() => onNavigateSection('recommendations')}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium"
              >
                View matrix <ChevronRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          {top_opportunities.length === 0 ? (
            <div className="text-xs text-slate-500 py-6 text-center">No strategic opportunities identified.</div>
          ) : (
            <div className="space-y-3">
              {top_opportunities.slice(0, 3).map((o, idx) => (
                <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        {o.potential_value}
                      </span>
                      <span className="text-xs font-semibold text-slate-200">{o.title}</span>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">Lever: <strong>{o.lever}</strong> • Effort: {o.effort}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Active Executive Alerts List */}
      {active_alerts && active_alerts.length > 0 && (
        <div className="bg-slate-900/60 backdrop-blur-md border border-amber-500/30 rounded-2xl p-5 shadow-lg">
          <div className="flex items-center gap-2 mb-3">
            <AlertOctagon className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-bold text-white">Active Executive Alerts</h3>
          </div>
          <div className="space-y-2">
            {active_alerts.map((al) => (
              <div key={al.id} className="p-3 bg-amber-950/20 border border-amber-800/30 rounded-xl flex items-start justify-between gap-3 text-xs">
                <div>
                  <div className="font-semibold text-amber-200">{al.title}</div>
                  <div className="text-amber-300/80 mt-0.5">{al.description}</div>
                </div>
                {al.target_section && onNavigateSection && (
                  <button
                    onClick={() => onNavigateSection(al.target_section!)}
                    className="px-2.5 py-1 text-[11px] font-medium bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/30 rounded-lg transition-colors shrink-0"
                  >
                    Inspect
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};
