import React, { useState, useEffect } from 'react';
import { Download, ExternalLink, FileText, Loader2, X } from 'lucide-react';
import { reportingApi } from '../../../api';

interface ReportPreviewModalProps {
  reportId: string | null;
  onClose: () => void;
}

export const ReportPreviewModal: React.FC<ReportPreviewModalProps> = ({
  reportId,
  onClose,
}) => {
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reportId) return;

    let mounted = true;
    setLoading(true);
    setError(null);

    reportingApi
      .getReport(reportId)
      .then((res) => {
        if (mounted) {
          setReport(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || 'Failed to load report preview');
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [reportId]);

  if (!reportId) return null;

  const downloadUrl = reportingApi.downloadReportUrl(reportId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-xl">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white truncate">
                {report?.title || 'Board Intelligence Report Preview'}
              </h2>
              <div className="text-xs text-slate-400 flex items-center gap-2 mt-0.5">
                <span>Format: <strong>{report?.export_format || 'HTML / PDF'}</strong></span>
                <span>•</span>
                <span>Type: <strong>{report?.report_type || 'EXECUTIVE_SUMMARY'}</strong></span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <a
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg flex items-center gap-1.5 shadow-sm transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              Download PDF
            </a>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-950">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
              <p className="text-sm">Rendering high-fidelity report preview...</p>
            </div>
          ) : error ? (
            <div className="h-full flex flex-col items-center justify-center text-rose-400 gap-2">
              <p className="text-sm font-semibold">{error}</p>
              <button
                onClick={onClose}
                className="mt-2 px-3 py-1.5 text-xs bg-slate-800 text-slate-300 rounded-lg"
              >
                Close
              </button>
            </div>
          ) : (
            <div className="bg-white text-slate-900 rounded-xl p-8 shadow-inner max-w-4xl mx-auto min-h-[600px] prose prose-slate">
              {report?.content_html ? (
                <div dangerouslySetInnerHTML={{ __html: report.content_html }} />
              ) : (
                <div className="text-slate-500 text-sm italic">
                  Report generated successfully. Click &quot;Download PDF&quot; above to view the formatted export package.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
