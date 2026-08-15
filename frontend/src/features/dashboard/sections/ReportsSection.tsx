import React from 'react';
import {
  Download,
  Eye,
  FileCheck2,
  FileText,
  Layers,
  Sparkles,
} from 'lucide-react';
import { ReportsSummaryItem } from '../../../types/dashboard';
import { reportingApi } from '../../../api';

interface ReportsSectionProps {
  reportsSummary: ReportsSummaryItem;
  onOpenPreview: (reportId: string) => void;
}

export const ReportsSection: React.FC<ReportsSectionProps> = ({
  reportsSummary,
  onOpenPreview,
}) => {
  const reports = reportsSummary?.reports || [];

  const getFormatBadge = (fmt: string) => {
    switch (fmt.toUpperCase()) {
      case 'PDF':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/30';
      case 'HTML':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'JSON':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <section id="reports" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-cyan-600 rounded-xl text-white shadow-lg">
            <FileCheck2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Boardroom Reports & Export Packages
            </h2>
            <p className="text-xs text-slate-400">
              Audit-ready intelligence briefs with instant HTML interactive preview and direct PDF download
            </p>
          </div>
        </div>
      </div>

      {/* Reports Table Card */}
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        {reports.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">
            No report packages exported yet for this dataset.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[10px] text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Report Title</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">File Size</th>
                  <th className="py-3 px-4">Generated Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {reports.map((r) => {
                  const downloadUrl = reportingApi.downloadReportUrl(r.report_id);
                  return (
                    <tr key={r.report_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4 font-semibold text-white flex items-center gap-2">
                        <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                        <span className="truncate max-w-xs">{r.title}</span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 uppercase font-mono text-[11px]">
                        {r.report_type}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 text-[10px] font-bold rounded-md border ${getFormatBadge(
                            r.export_format
                          )}`}
                        >
                          {r.export_format}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">
                        {(r.file_size_bytes / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-3.5 px-4 text-slate-400">
                        {r.generated_at ? new Date(r.generated_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-2">
                        <button
                          onClick={() => onOpenPreview(r.report_id)}
                          className="px-2.5 py-1 text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg inline-flex items-center gap-1 transition-all"
                        >
                          <Eye className="w-3.5 h-3.5 text-cyan-400" />
                          Preview
                        </button>
                        <a
                          href={downloadUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 text-[11px] font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg inline-flex items-center gap-1 shadow-sm transition-all"
                        >
                          <Download className="w-3.5 h-3.5" />
                          PDF
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
};
