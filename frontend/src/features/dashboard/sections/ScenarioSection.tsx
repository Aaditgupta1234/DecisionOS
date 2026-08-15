import React, { useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  GitBranch,
  Layers,
  Play,
  Sliders,
  Sparkles,
} from 'lucide-react';
import { ScenarioItem } from '../../../types/dashboard';

interface ScenarioSectionProps {
  scenarios: ScenarioItem[];
}

export const ScenarioSection: React.FC<ScenarioSectionProps> = ({ scenarios }) => {
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(
    scenarios[0]?.scenario_id || ''
  );

  const activeScenario =
    scenarios.find((s) => s.scenario_id === selectedScenarioId) || scenarios[0];

  if (!scenarios || scenarios.length === 0) {
    return (
      <section id="scenarios" className="scroll-mt-24 space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-purple-600 to-indigo-600 rounded-xl text-white shadow-lg">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Scenario Simulations & What-If Analysis
            </h2>
            <p className="text-xs text-slate-400">
              Deterministic causal simulation projections
            </p>
          </div>
        </div>
        <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
          No scenario simulations executed yet for this dataset.
        </div>
      </section>
    );
  }

  const chartData = (activeScenario.impacted_metrics || []).map((m) => ({
    name: m.metric_name || m.metric_key,
    Baseline: m.baseline_value,
    Simulated: m.simulated_value,
    deltaPct: m.delta_percentage,
  }));

  return (
    <section id="scenarios" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-purple-600 to-indigo-600 rounded-xl text-white shadow-lg">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Scenario Simulations & What-If Analysis
            </h2>
            <p className="text-xs text-slate-400">
              Comparative simulated trajectories and sensitivity adjustments
            </p>
          </div>
        </div>

        {/* Scenario Selector Tabs */}
        {scenarios.length > 1 && (
          <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-slate-800 rounded-xl self-start sm:self-auto overflow-x-auto">
            {scenarios.map((s) => (
              <button
                key={s.scenario_id}
                onClick={() => setSelectedScenarioId(s.scenario_id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all whitespace-nowrap ${
                  activeScenario.scenario_id === s.scenario_id
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {s.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Scenario Card */}
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        {/* Header & Levers */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 text-xs font-bold rounded-md bg-purple-500/20 text-purple-300 border border-purple-500/30">
                {activeScenario.scenario_type.replace('_', ' ')}
              </span>
              <span className="text-xs text-slate-400">
                Confidence: <strong className="text-slate-200">{Math.round(activeScenario.confidence_score * 100)}%</strong>
              </span>
            </div>
            <h3 className="text-lg font-bold text-white mt-2">{activeScenario.name}</h3>
            <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
              {activeScenario.description || activeScenario.impact_summary}
            </p>
          </div>

          {/* Sensitivity Adjustments Chips */}
          {activeScenario.sensitivity_adjustments && activeScenario.sensitivity_adjustments.length > 0 && (
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 shrink-0">
              <div className="text-[10px] text-slate-500 font-semibold uppercase mb-1 flex items-center gap-1">
                <Sliders className="w-3 h-3 text-purple-400" />
                Sensitivity Levers
              </div>
              <div className="flex flex-wrap gap-1.5 max-w-xs">
                {activeScenario.sensitivity_adjustments.map((adj, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-800 text-purple-300 border border-purple-900/40"
                  >
                    {adj.lever || adj.param}: <strong>{adj.delta || adj.value}</strong>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Baseline vs Simulated Comparison Bar Chart */}
        {chartData.length > 0 && (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickFormatter={(v) => (v >= 1000000 ? `$${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `$${(v / 1000).toFixed(0)}K` : `${v}`)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="Baseline" fill="#475569" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Simulated" fill="#a855f7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Impacted Metrics Cards */}
        {activeScenario.impacted_metrics && activeScenario.impacted_metrics.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
            {activeScenario.impacted_metrics.map((m, idx) => {
              const isPositive = m.delta_percentage >= 0;
              return (
                <div
                  key={idx}
                  className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-center justify-between"
                >
                  <div>
                    <span className="text-xs font-semibold text-slate-400 block">
                      {m.metric_name || m.metric_key}
                    </span>
                    <div className="text-base font-bold text-white mt-0.5">
                      ${m.simulated_value.toLocaleString()}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      Baseline: ${m.baseline_value.toLocaleString()}
                    </div>
                  </div>
                  <div
                    className={`flex items-center text-xs font-bold px-2 py-1 rounded-lg ${
                      isPositive
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}
                  >
                    {isPositive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                    {m.delta_percentage > 0 ? `+${m.delta_percentage}%` : `${m.delta_percentage}%`}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
};
