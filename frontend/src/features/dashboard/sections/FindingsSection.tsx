import React, { useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  FileSearch,
  Filter,
  Info,
  ShieldAlert,
} from 'lucide-react';
import { FindingItem } from '../../../types/dashboard';

interface FindingsSectionProps {
  findings: FindingItem[];
}

export const FindingsSection: React.FC<FindingsSectionProps> = ({ findings }) => {
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

  const filteredFindings =
    selectedSeverity === 'ALL'
      ? findings
      : findings.filter((f) => f.severity.toUpperCase() === selectedSeverity);

  const getSeverityBadge = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'LOW':
        return 'bg-slate-700/50 text-slate-300 border-slate-600';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section id="findings" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-rose-600 to-amber-600 rounded-xl text-white shadow-lg">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Diagnostic Findings & Anomalies
            </h2>
            <p className="text-xs text-slate-400">
              Verified operational anomalies, revenue contractions, and efficiency frictions identified by diagnostic engines
            </p>
          </div>
        </div>

        {/* Severity Filter Tabs */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-slate-800 rounded-xl self-start sm:self-auto overflow-x-auto">
          {severities.map((sev) => {
            const count =
              sev === 'ALL'
                ? findings.length
                : findings.filter((f) => f.severity.toUpperCase() === sev).length;
            return (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all capitalize whitespace-nowrap flex items-center gap-1.5 ${
                  selectedSeverity === sev
                    ? 'bg-gradient-to-r from-rose-600 to-amber-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <span>{sev.toLowerCase()}</span>
                <span className="text-[10px] opacity-75 font-mono">({count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Findings List */}
      {filteredFindings.length === 0 ? (
        <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl text-slate-500 text-sm">
          No diagnostic findings match severity &quot;{selectedSeverity}&quot;.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredFindings.map((finding) => {
            const isExpanded = expandedId === finding.finding_id;
            return (
              <div
                key={finding.finding_id}
                className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-lg hover:border-slate-700 transition-all"
              >
                <div
                  className="flex items-start justify-between gap-4 cursor-pointer"
                  onClick={() => toggleExpand(finding.finding_id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={`px-2.5 py-0.5 text-xs font-bold rounded-md border ${getSeverityBadge(
                          finding.severity
                        )}`}
                      >
                        {finding.severity}
                      </span>
                      <span className="text-xs text-slate-500 uppercase font-mono">
                        {finding.finding_type}
                      </span>
                      {finding.category && (
                        <span className="text-xs text-slate-400 font-medium">
                          • {finding.category}
                        </span>
                      )}
                    </div>
                    <h3 className="text-base font-bold text-white mt-2">
                      {finding.title}
                    </h3>
                    <p className="text-xs text-slate-300 mt-1 line-clamp-2">
                      {finding.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <div className="text-right hidden sm:block">
                      <div className="text-xs font-bold text-slate-200">
                        Impact: {Math.round(finding.impact_score * 100)}%
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Confidence: {Math.round(finding.confidence_score * 100)}%
                      </div>
                    </div>
                    <button className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors">
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Expandable Details */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-slate-800/80 space-y-3 animate-in fade-in">
                    {finding.business_impact && (
                      <div className="p-3 bg-rose-950/20 border border-rose-900/30 rounded-xl text-xs">
                        <strong className="text-rose-300 font-semibold block mb-0.5">
                          Business & Financial Impact:
                        </strong>
                        <span className="text-slate-300">{finding.business_impact}</span>
                      </div>
                    )}

                    {finding.evidence_points && finding.evidence_points.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                          Observed Evidence & Telemetry:
                        </div>
                        <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 bg-slate-950/40 p-3 rounded-xl border border-slate-800/60">
                          {finding.evidence_points.map((ev, i) => (
                            <li key={i}>{ev}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2">
                      <span>Finding Identifier: <code className="font-mono text-slate-400">{finding.finding_id.slice(0, 12)}...</code></span>
                      {finding.primary_metric_key && (
                        <span>Linked KPI: <strong className="text-cyan-400">{finding.primary_metric_key}</strong></span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
