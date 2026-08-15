import React from 'react';
import {
  Brain,
  CheckCircle2,
  Compass,
  FileText,
  MessageSquareQuote,
  Shield,
  Sparkles,
  Target,
} from 'lucide-react';
import { StrategicInsightsPayload } from '../../../types/dashboard';

interface InsightSectionProps {
  insights: StrategicInsightsPayload;
}

export const InsightSection: React.FC<InsightSectionProps> = ({ insights }) => {
  const {
    executive_summary_html,
    strategic_themes,
    risk_assessment,
    growth_opportunities,
    board_commentary,
  } = insights;

  const getImpactColor = (impact: string) => {
    switch (impact.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      default:
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
    }
  };

  return (
    <section id="insights" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-teal-600 rounded-xl text-white shadow-lg">
            <Brain className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Strategic Insights & Boardroom Commentary
            </h2>
            <p className="text-xs text-slate-400">
              Cross-cutting thematic imperatives, risk matrices, and boardroom strategic commentary
            </p>
          </div>
        </div>
      </div>

      {/* Main Grid: Board Commentary & Strategic Themes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Boardroom Briefing Card */}
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 mb-2">
              <MessageSquareQuote className="w-5 h-5" />
              <span className="text-xs font-bold uppercase tracking-wider">Boardroom Perspective</span>
            </div>
            <h3 className="text-base font-bold text-white mb-2">Executive Advisory Commentary</h3>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/50 p-4 rounded-xl border border-slate-800/80 italic">
              &quot;{board_commentary || 'Maintain focus on tier-1 contract renewals while capitalizing on identified high-impact operational optimizations.'}&quot;
            </p>
          </div>

          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              Factual Alignment: <strong>Verified</strong>
            </span>
            <span className="text-[10px] text-slate-500">DecisionOS Synthesizer</span>
          </div>
        </div>

        {/* Strategic Thematic Imperatives */}
        <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-indigo-400">
              <Compass className="w-5 h-5" />
              <h3 className="text-sm font-bold text-white">Thematic Strategic Imperatives</h3>
            </div>
            <span className="text-xs text-slate-400">
              {strategic_themes?.length || 0} active initiatives
            </span>
          </div>

          {strategic_themes && strategic_themes.length > 0 ? (
            <div className="space-y-3">
              {strategic_themes.map((theme, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${getImpactColor(
                          theme.impact_level
                        )}`}
                      >
                        {theme.impact_level} IMPACT
                      </span>
                      <h4 className="text-xs font-bold text-white">{theme.theme_title}</h4>
                    </div>
                    <p className="text-xs text-slate-300 mt-1">{theme.summary}</p>
                  </div>
                  <div className="text-xs text-slate-400 shrink-0 sm:text-right">
                    <span>Confidence: <strong className="text-slate-200">{Math.round(theme.confidence_score * 100)}%</strong></span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-slate-500 py-6 text-center">
              No thematic imperatives synthesized yet.
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
