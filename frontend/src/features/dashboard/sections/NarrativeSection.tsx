import React, { useState } from 'react';
import { BookOpen, Calendar, Clock, FileText, Sparkles, UserCheck } from 'lucide-react';
import { NarrativeReportItem } from '../../../types/dashboard';

interface NarrativeSectionProps {
  narratives: NarrativeReportItem[];
}

export const NarrativeSection: React.FC<NarrativeSectionProps> = ({ narratives }) => {
  const [selectedReportId, setSelectedReportId] = useState<string>(
    narratives[0]?.report_id || ''
  );

  const activeNarrative =
    narratives.find((n) => n.report_id === selectedReportId) || narratives[0];

  if (!narratives || narratives.length === 0) {
    return (
      <section id="narratives" className="scroll-mt-24 space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-pink-600 rounded-xl text-white shadow-lg">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              AI Strategic Executive Briefings
            </h2>
            <p className="text-xs text-slate-400">
              Board-ready synthesized narratives and decision commentaries
            </p>
          </div>
        </div>
        <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
          No AI executive narratives synthesized yet for this dataset.
        </div>
      </section>
    );
  }

  return (
    <section id="narratives" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-pink-600 rounded-xl text-white shadow-lg">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              AI Strategic Executive Briefings
            </h2>
            <p className="text-xs text-slate-400">
              Synthesized natural language narratives customized for board and C-suite audiences
            </p>
          </div>
        </div>

        {/* Narrative Selector Tabs */}
        {narratives.length > 1 && (
          <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-slate-800 rounded-xl self-start sm:self-auto overflow-x-auto">
            {narratives.map((n) => (
              <button
                key={n.report_id}
                onClick={() => setSelectedReportId(n.report_id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all whitespace-nowrap ${
                  activeNarrative.report_id === n.report_id
                    ? 'bg-gradient-to-r from-indigo-600 to-pink-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {n.title || n.narrative_type}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Narrative Content Card */}
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        {/* Header Metadata */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 text-xs font-bold rounded-md bg-pink-500/20 text-pink-300 border border-pink-500/30">
                {activeNarrative.audience_level || 'EXECUTIVE'}
              </span>
              <span className="text-xs text-slate-500 uppercase font-mono">
                {activeNarrative.narrative_type}
              </span>
            </div>
            <h3 className="text-lg font-bold text-white mt-1">{activeNarrative.title}</h3>
          </div>

          <div className="text-xs text-slate-400 flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>Generated: {new Date(activeNarrative.generated_at).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Rich HTML Content Body */}
        <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-6 text-slate-200 text-sm leading-relaxed prose prose-invert max-w-none prose-p:my-2 prose-headings:text-white">
          <div dangerouslySetInnerHTML={{ __html: activeNarrative.content_html }} />
        </div>
      </div>
    </section>
  );
};
