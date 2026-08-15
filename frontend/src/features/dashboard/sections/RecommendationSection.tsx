import React, { useState } from 'react';
import {
  CheckSquare,
  ChevronDown,
  ChevronUp,
  Clock,
  Flame,
  Grid2X2,
  Lightbulb,
  Sparkles,
  Target,
  Zap,
} from 'lucide-react';
import { RecommendationMatrixItem } from '../../../types/dashboard';

interface RecommendationSectionProps {
  recommendations: RecommendationMatrixItem[];
}

export const RecommendationSection: React.FC<RecommendationSectionProps> = ({
  recommendations,
}) => {
  const [selectedQuadrant, setSelectedQuadrant] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const quadrants = [
    { id: 'ALL', label: 'All Quadrants' },
    { id: 'QUICK_WIN', label: 'Quick Wins (High Impact, Low Effort)' },
    { id: 'MAJOR_PROJECT', label: 'Major Projects (High Impact, High Effort)' },
    { id: 'FILL_IN', label: 'Fill-ins (Low Impact, Low Effort)' },
    { id: 'DEPRIORITIZED', label: 'Deprioritized (Low Impact, High Effort)' },
  ];

  const filteredRecs =
    selectedQuadrant === 'ALL'
      ? recommendations
      : recommendations.filter((r) => r.quadrant === selectedQuadrant);

  const getQuadrantBadge = (quadrant: string) => {
    switch (quadrant) {
      case 'QUICK_WIN':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'MAJOR_PROJECT':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'FILL_IN':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'DEPRIORITIZED':
        return 'bg-slate-700/50 text-slate-300 border-slate-600';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toUpperCase()) {
      case 'CRITICAL':
        return 'text-rose-400';
      case 'HIGH':
        return 'text-amber-400';
      case 'MEDIUM':
        return 'text-cyan-400';
      default:
        return 'text-slate-400';
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section id="recommendations" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-emerald-600 to-cyan-600 rounded-xl text-white shadow-lg">
            <Lightbulb className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Strategic Recommendations Matrix
            </h2>
            <p className="text-xs text-slate-400">
              Prioritized 2x2 action roadmap with impact vs effort evaluation, execution steps, and time-to-value estimates
            </p>
          </div>
        </div>

        {/* Quadrant Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-slate-800 rounded-xl self-start sm:self-auto overflow-x-auto">
          {quadrants.map((q) => (
            <button
              key={q.id}
              onClick={() => setSelectedQuadrant(q.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all whitespace-nowrap ${
                selectedQuadrant === q.id
                  ? 'bg-gradient-to-r from-emerald-600 to-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {q.id === 'ALL' ? 'All' : q.id.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Recommendations List */}
      {filteredRecs.length === 0 ? (
        <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
          No recommendations found for selected quadrant.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredRecs.map((rec) => {
            const isExpanded = expandedId === rec.recommendation_id;
            return (
              <div
                key={rec.recommendation_id}
                className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between hover:border-slate-700 transition-all"
              >
                <div>
                  {/* Top Badges */}
                  <div className="flex items-center justify-between gap-2 flex-wrap mb-3">
                    <span
                      className={`px-2.5 py-0.5 text-xs font-bold rounded-md border ${getQuadrantBadge(
                        rec.quadrant
                      )}`}
                    >
                      {rec.quadrant.replace('_', ' ')}
                    </span>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {rec.estimated_time_to_value}
                      </span>
                      <span className={`font-bold ${getPriorityColor(rec.priority)}`}>
                        {rec.priority}
                      </span>
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white">{rec.title}</h3>

                  {/* Impact vs Effort Scores */}
                  <div className="grid grid-cols-2 gap-3 mt-4">
                    <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Impact Score</div>
                      <div className="text-sm font-bold text-emerald-400 mt-0.5">
                        {Math.round(rec.impact_score * 100)}%
                      </div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80">
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Effort Score</div>
                      <div className="text-sm font-bold text-cyan-400 mt-0.5">
                        {Math.round(rec.effort_score * 100)}%
                      </div>
                    </div>
                  </div>

                  {rec.expected_benefit && (
                    <div className="mt-3 text-xs text-slate-300 bg-emerald-950/20 p-2.5 rounded-xl border border-emerald-900/30">
                      <strong className="text-emerald-300 font-semibold block mb-0.5">Expected Benefit:</strong>
                      {rec.expected_benefit}
                    </div>
                  )}
                </div>

                {/* Expandable Action Plan */}
                <div className="mt-4 pt-3 border-t border-slate-800/80">
                  <button
                    onClick={() => toggleExpand(rec.recommendation_id)}
                    className="w-full flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white py-1"
                  >
                    <span>Action Plan ({rec.action_plan?.length || 0} steps)</span>
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  {isExpanded && rec.action_plan && (
                    <div className="mt-2 space-y-2 animate-in fade-in">
                      {rec.action_plan.map((step, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 p-2 bg-slate-950/40 rounded-lg border border-slate-800/60 text-xs text-slate-300"
                        >
                          <CheckSquare className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
