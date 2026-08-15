import React, { useState } from 'react';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Download,
  FileText,
  HelpCircle,
  Layers,
  RefreshCw,
  Shield,
  Zap,
} from 'lucide-react';
import { WorkspaceResponse } from '../../../types/dashboard';

interface DashboardHeaderProps {
  data: WorkspaceResponse;
  isRefreshing: boolean;
  onRefresh: () => void;
  onOpenReportModal?: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({
  data,
  isRefreshing,
  onRefresh,
  onOpenReportModal,
}) => {
  const { metadata, dashboard_health, warnings } = data;
  const [showMeta, setShowMeta] = useState(false);

  const getStatusBadge = () => {
    switch (metadata.status) {
      case 'READY':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Snapshot Active
          </span>
        );
      case 'BUILDING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            Generating Intelligence...
          </span>
        );
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3.5 h-3.5" />
            Queued in Pipeline
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertCircle className="w-3.5 h-3.5" />
            Build Failed
          </span>
        );
      default:
        return null;
    }
  };

  const getHealthBadge = () => {
    if (dashboard_health.status === 'HEALTHY') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-md bg-emerald-950/60 text-emerald-300 border border-emerald-800/40">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Healthy
        </span>
      );
    }
    if (dashboard_health.status === 'PARTIAL') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-md bg-amber-950/60 text-amber-300 border border-amber-800/40">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          {dashboard_health.stale ? 'Stale Data' : 'Partial Warnings'}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-md bg-rose-950/60 text-rose-300 border border-rose-800/40">
        <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
        Degraded ({dashboard_health.warnings_count} issues)
      </span>
    );
  };

  return (
    <header className="sticky top-0 z-30 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/80 px-6 py-4 transition-all">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Title & Dataset metadata */}
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-indigo-600 rounded-xl text-white shadow-lg shadow-cyan-900/30">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h1 className="text-xl font-bold tracking-tight text-white">
                Executive Intelligence Workspace
              </h1>
              {getStatusBadge()}
              {getHealthBadge()}
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400 mt-1 flex-wrap">
              <span className="text-slate-300 font-medium">{metadata.dataset_name}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-500" />
                Snapshot age: <strong className="text-slate-300 font-mono">{metadata.age_seconds < 60 ? `${metadata.age_seconds}s` : `${Math.floor(metadata.age_seconds / 60)}m`}</strong>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Zap className="w-3 h-3 text-cyan-400" />
                {metadata.cache_hit ? 'Served from Cache' : 'Rebuilt from Read-Model'}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3 self-end md:self-center flex-wrap">
          {/* Metadata Inspector Trigger */}
          <button
            onClick={() => setShowMeta(!showMeta)}
            className="px-3 py-2 text-xs font-medium text-slate-300 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-xl transition-all flex items-center gap-1.5"
            title="Inspect SHA-256 hash and build provenance"
          >
            <Shield className="w-3.5 h-3.5 text-cyan-400" />
            <span>Provenance</span>
          </button>

          {/* In-app Reports */}
          {onOpenReportModal && (
            <button
              onClick={onOpenReportModal}
              className="px-3.5 py-2 text-xs font-medium text-slate-200 hover:text-white bg-slate-800/90 hover:bg-slate-700 border border-slate-700/80 rounded-xl transition-all flex items-center gap-1.5 shadow-sm"
            >
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              <span>Board Package</span>
            </button>
          )}

          {/* Refresh Snapshot Button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing || metadata.status === 'BUILDING'}
            className="px-4 py-2 text-xs font-semibold text-white bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all flex items-center gap-2 shadow-lg shadow-cyan-950/50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>{isRefreshing ? 'Refreshing...' : 'Refresh Workspace'}</span>
          </button>
        </div>
      </div>

      {/* Provenance Panel Expandable */}
      {showMeta && (
        <div className="max-w-7xl mx-auto mt-4 p-4 rounded-xl bg-slate-900/90 border border-slate-800/80 text-xs text-slate-300 grid grid-cols-2 md:grid-cols-4 gap-4 animate-in fade-in slide-in-from-top-2">
          <div>
            <span className="text-slate-500 block mb-0.5">Snapshot Hash (SHA-256)</span>
            <code className="font-mono text-cyan-300 text-[11px] block truncate" title={metadata.snapshot_hash}>
              {metadata.snapshot_hash}
            </code>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5">Build Performance</span>
            <span className="font-semibold text-slate-200">{metadata.build_time_ms} ms</span>
            <span className="text-slate-400 ml-1">({(metadata.snapshot_size_bytes / 1024).toFixed(1)} KB)</span>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5">Verified Artifacts Aggregated</span>
            <span className="font-semibold text-slate-200">{metadata.artifact_count} artifacts</span>
          </div>
          <div>
            <span className="text-slate-500 block mb-0.5">Engine Versions</span>
            <span className="text-slate-300 font-mono">Workspace v{metadata.workspace_version} • Questions v{metadata.question_generation_version}</span>
          </div>
        </div>
      )}

      {/* Stale or Degraded Warning Banner */}
      {warnings.length > 0 && (
        <div className="max-w-7xl mx-auto mt-3 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="font-medium text-amber-200">Workspace Advisories:</div>
            <ul className="list-disc list-inside mt-0.5 space-y-0.5 text-amber-300/90">
              {warnings.map((w, idx) => (
                <li key={idx}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </header>
  );
};
