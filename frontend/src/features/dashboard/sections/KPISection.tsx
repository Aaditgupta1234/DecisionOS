import React, { useState } from 'react';
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  Filter,
  Minus,
  TrendingUp,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { KPIMetricItem } from '../../../types/dashboard';

interface KPISectionProps {
  kpis: KPIMetricItem[];
}

export const KPISection: React.FC<KPISectionProps> = ({ kpis }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = ['ALL', ...Array.from(new Set(kpis.map((k) => k.category)))];

  const filteredKPIs =
    selectedCategory === 'ALL'
      ? kpis
      : kpis.filter((k) => k.category === selectedCategory);

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'OPTIMAL':
      case 'HEALTHY':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'WARNING':
      case 'WATCH_LIST':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'CRITICAL':
      case 'AT_RISK':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      default:
        return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  return (
    <section id="kpis" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-xl text-white shadow-lg">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Key Performance Indicators
            </h2>
            <p className="text-xs text-slate-400">
              Verified metric aggregates with historical micro-trajectories and performance confidence
            </p>
          </div>
        </div>

        {/* Category Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-slate-800 rounded-xl self-start sm:self-auto overflow-x-auto max-w-full">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all capitalize whitespace-nowrap ${
                selectedCategory === cat
                  ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {cat.toLowerCase().replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards Grid */}
      {filteredKPIs.length === 0 ? (
        <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
          No metrics available for category &quot;{selectedCategory}&quot;.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredKPIs.map((kpi) => {
            const hasHistory = kpi.historical_trend && kpi.historical_trend.length > 1;
            const trendUp = kpi.trend === 'UP';
            const trendDown = kpi.trend === 'DOWN';

            return (
              <div
                key={kpi.metric_key}
                className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between hover:border-slate-700 transition-all group"
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        {kpi.category}
                      </span>
                      <h3 className="text-sm font-bold text-white mt-0.5 group-hover:text-cyan-300 transition-colors">
                        {kpi.metric_name}
                      </h3>
                    </div>
                    <span
                      className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${getStatusColor(
                        kpi.status
                      )}`}
                    >
                      {kpi.status}
                    </span>
                  </div>

                  {/* Metric Value & Delta */}
                  <div className="mt-4 flex items-baseline justify-between">
                    <div className="text-2xl font-black text-white tracking-tight">
                      {kpi.formatted_value}
                    </div>
                    {kpi.trend_percentage !== 0 && (
                      <span
                        className={`inline-flex items-center text-xs font-bold ${
                          trendUp ? 'text-emerald-400' : trendDown ? 'text-rose-400' : 'text-slate-400'
                        }`}
                      >
                        {trendUp ? (
                          <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
                        ) : trendDown ? (
                          <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                        ) : (
                          <Minus className="w-3.5 h-3.5 mr-0.5" />
                        )}
                        {kpi.trend_percentage > 0 ? `+${kpi.trend_percentage}%` : `${kpi.trend_percentage}%`}
                      </span>
                    )}
                  </div>
                </div>

                {/* Micro Sparkline Recharts */}
                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  {hasHistory ? (
                    <div className="h-16 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={kpi.historical_trend}>
                          <defs>
                            <linearGradient id={`grad-${kpi.metric_key}`} x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                              <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                            </linearGradient>
                          </defs>
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#0f172a',
                              borderColor: '#334155',
                              borderRadius: '0.5rem',
                              fontSize: '11px',
                              color: '#f8fafc',
                            }}
                          />
                          <Area
                            type="monotone"
                            dataKey="value"
                            stroke="#06b6d4"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill={`url(#grad-${kpi.metric_key})`}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="text-[11px] text-slate-500 py-2">
                      Historical baseline established.
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2">
                    <span>Confidence: <strong>{Math.round(kpi.confidence_score * 100)}%</strong></span>
                    {kpi.target_value && <span>Target: {kpi.target_value} {kpi.unit}</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
