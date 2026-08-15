import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { dashboardApi } from '../../api';
import { WorkspaceResponse } from '../../types/dashboard';
import { DashboardHeader } from './components/DashboardHeader';
import { DashboardSidebar } from './components/DashboardSidebar';
import { DashboardSectionErrorBoundary } from './components/DashboardSectionErrorBoundary';
import { ReportPreviewModal } from './components/ReportPreviewModal';
import { OverviewSection } from './sections/OverviewSection';
import { KPISection } from './sections/KPISection';
import { FindingsSection } from './sections/FindingsSection';
import { RootCauseSection } from './sections/RootCauseSection';
import { RecommendationSection } from './sections/RecommendationSection';
import { ForecastSection } from './sections/ForecastSection';
import { ScenarioSection } from './sections/ScenarioSection';
import { NarrativeSection } from './sections/NarrativeSection';
import { InsightSection } from './sections/InsightSection';
import { ReportsSection } from './sections/ReportsSection';
import { ChatSection } from './sections/ChatSection';

interface ExecutiveDashboardProps {
  datasetId: string;
}

export const ExecutiveDashboard: React.FC<ExecutiveDashboardProps> = ({ datasetId }) => {
  const [data, setData] = useState<WorkspaceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [previewReportId, setPreviewReportId] = useState<string | null>(null);

  // Telemetry buffer: Batched every 30 seconds
  const telemetryBufferRef = useRef<Array<{ section: string; viewed_at: string }>>([]);

  // Fetch full workspace state
  const loadWorkspace = useCallback(async (isRefresh = false) => {
    try {
      if (!isRefresh) setLoading(true);
      setError(null);

      const res = await dashboardApi.getWorkspace(datasetId);
      setData(res);

      // If status is BUILDING or PENDING, poll for completion
      if (res.metadata?.status === 'BUILDING' || res.metadata?.status === 'PENDING') {
        pollStatus();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load executive workspace.');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [datasetId]);

  // Status Poller
  const pollStatus = useCallback(() => {
    const interval = setInterval(async () => {
      try {
        const stat = await dashboardApi.getStatus(datasetId);
        if (stat.snapshot_status === 'READY' || stat.snapshot_status === 'FAILED') {
          clearInterval(interval);
          loadWorkspace(true);
        }
      } catch {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [datasetId, loadWorkspace]);

  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  // Handle explicit snapshot refresh
  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      const res = await dashboardApi.refreshSnapshot(datasetId, 'MANUAL');
      if (res.status === 'READY') {
        await loadWorkspace(true);
      } else {
        pollStatus();
      }
    } catch (err: any) {
      console.error('Refresh failed:', err);
      setIsRefreshing(false);
    }
  };

  // Scroll spy via IntersectionObserver
  useEffect(() => {
    const sectionIds = [
      'overview',
      'kpis',
      'findings',
      'root_causes',
      'recommendations',
      'forecasts',
      'scenarios',
      'narratives',
      'insights',
      'reports',
      'chat',
    ];

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.find((e) => e.isIntersecting);
        if (visible) {
          const id = visible.target.id;
          setActiveSection(id);
          // Record view event in telemetry buffer
          telemetryBufferRef.current.push({
            section: id,
            viewed_at: new Date().toISOString(),
          });
        }
      },
      {
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0,
      }
    );

    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [data]);

  // Telemetry flush timer: Every 30 seconds
  useEffect(() => {
    const flushInterval = setInterval(() => {
      if (telemetryBufferRef.current.length > 0) {
        const eventsToSend = [...telemetryBufferRef.current];
        telemetryBufferRef.current = [];
        dashboardApi
          .recordTelemetry(datasetId, eventsToSend)
          .catch((err) => console.warn('Telemetry sync error:', err));
      }
    }, 30000);

    return () => clearInterval(flushInterval);
  }, [datasetId]);

  // Scroll to section smoothly
  const handleSelectSection = (sectionId: string) => {
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-4 text-slate-400">
        <Loader2 className="w-10 h-10 animate-spin text-cyan-400" />
        <p className="text-sm font-medium">Synthesizing executive intelligence workspace...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center p-6">
        <div className="bg-slate-900/80 border border-rose-500/30 rounded-2xl p-8 max-w-lg text-center shadow-2xl">
          <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-white">Executive Workspace Unavailable</h2>
          <p className="text-xs text-slate-400 mt-2">{error || 'Could not load dataset workspace.'}</p>
          <button
            onClick={() => loadWorkspace()}
            className="mt-6 px-4 py-2 text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl shadow-lg transition-all"
          >
            Retry Hydration
          </button>
        </div>
      </div>
    );
  }

  const ws = data.workspace;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col pb-16">
      {/* Sticky Header */}
      <DashboardHeader
        data={data}
        isRefreshing={isRefreshing}
        onRefresh={handleRefresh}
        onOpenReportModal={() => {
          const latestId = data.workspace?.reports?.latest_report_id;
          if (latestId) setPreviewReportId(latestId);
        }}
      />

      {/* Main Continuous Layout: Sidebar + Sections */}
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 pt-6 flex gap-8">
        {/* Navigation Sidebar Spy */}
        <DashboardSidebar
          activeSection={activeSection}
          onSelectSection={handleSelectSection}
          stats={ws?.overview?.statistics}
        />

        {/* Continuous Sections Feed */}
        <main className="flex-1 min-w-0 space-y-12">
          {ws?.overview && (
            <DashboardSectionErrorBoundary
              title="Executive Scorecard & Health"
              sectionKey="overview"
              onRetry={() => loadWorkspace(true)}
            >
              <OverviewSection
                overview={ws.overview}
                onNavigateSection={handleSelectSection}
              />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.kpis && (
            <DashboardSectionErrorBoundary
              title="Key Performance Indicators"
              sectionKey="kpis"
              onRetry={() => loadWorkspace(true)}
            >
              <KPISection kpis={ws.kpis} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.findings && (
            <DashboardSectionErrorBoundary
              title="Diagnostic Findings"
              sectionKey="findings"
              onRetry={() => loadWorkspace(true)}
            >
              <FindingsSection findings={ws.findings} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.root_causes && (
            <DashboardSectionErrorBoundary
              title="Root Cause Chains"
              sectionKey="root_causes"
              onRetry={() => loadWorkspace(true)}
            >
              <RootCauseSection rootCauses={ws.root_causes} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.recommendations && (
            <DashboardSectionErrorBoundary
              title="Strategic Recommendations Matrix"
              sectionKey="recommendations"
              onRetry={() => loadWorkspace(true)}
            >
              <RecommendationSection recommendations={ws.recommendations} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.forecasts && (
            <DashboardSectionErrorBoundary
              title="Predictive Forecasts"
              sectionKey="forecasts"
              onRetry={() => loadWorkspace(true)}
            >
              <ForecastSection forecasts={ws.forecasts} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.scenarios && (
            <DashboardSectionErrorBoundary
              title="Scenario Simulations"
              sectionKey="scenarios"
              onRetry={() => loadWorkspace(true)}
            >
              <ScenarioSection scenarios={ws.scenarios} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.narratives && (
            <DashboardSectionErrorBoundary
              title="AI Executive Briefings"
              sectionKey="narratives"
              onRetry={() => loadWorkspace(true)}
            >
              <NarrativeSection narratives={ws.narratives} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.insights && (
            <DashboardSectionErrorBoundary
              title="Strategic Insights & Themes"
              sectionKey="insights"
              onRetry={() => loadWorkspace(true)}
            >
              <InsightSection insights={ws.insights} />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.reports && (
            <DashboardSectionErrorBoundary
              title="Boardroom Reports & Exports"
              sectionKey="reports"
              onRetry={() => loadWorkspace(true)}
            >
              <ReportsSection
                reportsSummary={ws.reports}
                onOpenPreview={(id) => setPreviewReportId(id)}
              />
            </DashboardSectionErrorBoundary>
          )}

          {ws?.chat && (
            <DashboardSectionErrorBoundary
              title="AI Decision Copilot"
              sectionKey="chat"
              onRetry={() => loadWorkspace(true)}
            >
              <ChatSection
                datasetId={datasetId}
                chatSummary={ws.chat}
              />
            </DashboardSectionErrorBoundary>
          )}
        </main>
      </div>

      {/* In-app Report Preview Modal */}
      <ReportPreviewModal
        reportId={previewReportId}
        onClose={() => setPreviewReportId(null)}
      />
    </div>
  );
};
export default ExecutiveDashboard;
