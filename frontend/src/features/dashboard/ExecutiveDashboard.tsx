import React, { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { dashboardApi } from '../../api';
import { WorkspaceResponse } from '../../types/dashboard';
import { DashboardHeader } from './components/DashboardHeader';
import { DashboardSidebar } from './components/DashboardSidebar';
import { DashboardSectionErrorBoundary } from './components/DashboardSectionErrorBoundary';
import { ReportPreviewModal } from './components/ReportPreviewModal';

// Immediate Hydration Sections (Core Executive Shell)
import { OverviewSection } from './sections/OverviewSection';
import { KPISection } from './sections/KPISection';
import { FindingsSection } from './sections/FindingsSection';
import { RootCauseSection } from './sections/RootCauseSection';
import { RecommendationSection } from './sections/RecommendationSection';
import { 
  KPICardSkeleton, 
  ChartSkeleton, 
  FindingsSkeleton, 
  TableSkeleton 
} from '../../design-system/skeletons';
import { FadeUp, FadeIn, CrossFade } from '../../design-system/motion';

// Code-Split Lazy Loaded Heavyweight Sections
const ForecastSection = React.lazy(() =>
  import('./sections/ForecastSection').then((m) => ({ default: m.ForecastSection }))
);
const ScenarioSection = React.lazy(() =>
  import('./sections/ScenarioSection').then((m) => ({ default: m.ScenarioSection }))
);
const NarrativeSection = React.lazy(() =>
  import('./sections/NarrativeSection').then((m) => ({ default: m.NarrativeSection }))
);
const InsightSection = React.lazy(() =>
  import('./sections/InsightSection').then((m) => ({ default: m.InsightSection }))
);
const ReportsSection = React.lazy(() =>
  import('./sections/ReportsSection').then((m) => ({ default: m.ReportsSection }))
);
const ChatSection = React.lazy(() =>
  import('./sections/ChatSection').then((m) => ({ default: m.ChatSection }))
);

const SectionSkeleton: React.FC<{ title: string }> = ({ title }) => (
  <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8 animate-pulse flex flex-col items-center justify-center text-center space-y-3 min-h-[220px]">
    <Loader2 className="w-6 h-6 text-cyan-400 animate-spin" />
    <span className="text-xs font-semibold text-slate-300">Loading {title}...</span>
    <span className="text-[11px] text-slate-500">Hydrating progressive intelligence module</span>
  </div>
);

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
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 pt-8 pb-16 space-y-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICardSkeleton />
          <KPICardSkeleton />
          <KPICardSkeleton />
          <KPICardSkeleton />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChartSkeleton height={240} />
          </div>
          <div>
            <FindingsSkeleton />
          </div>
        </div>
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

        {/* Continuous Sections Feed with Rapid 0/100/200/300ms Cascade */}
        <main className="flex-1 min-w-0 space-y-12">
          {ws?.overview && (
            <FadeUp delay={0}>
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
            </FadeUp>
          )}

          {ws?.kpis && (
            <FadeUp delay={0.1}>
              <DashboardSectionErrorBoundary
                title="Key Performance Indicators"
                sectionKey="kpis"
                onRetry={() => loadWorkspace(true)}
              >
                <KPISection kpis={ws.kpis} />
              </DashboardSectionErrorBoundary>
            </FadeUp>
          )}

          {ws?.findings && (
            <FadeUp delay={0.2}>
              <DashboardSectionErrorBoundary
                title="Diagnostic Findings"
                sectionKey="findings"
                onRetry={() => loadWorkspace(true)}
              >
                <FindingsSection findings={ws.findings} />
              </DashboardSectionErrorBoundary>
            </FadeUp>
          )}

          {ws?.root_causes && (
            <FadeUp delay={0.25}>
              <DashboardSectionErrorBoundary
                title="Root Cause Chains"
                sectionKey="root_causes"
                onRetry={() => loadWorkspace(true)}
              >
                <RootCauseSection rootCauses={ws.root_causes} />
              </DashboardSectionErrorBoundary>
            </FadeUp>
          )}

          {ws?.recommendations && (
            <FadeUp delay={0.3}>
              <DashboardSectionErrorBoundary
                title="Strategic Recommendations Matrix"
                sectionKey="recommendations"
                onRetry={() => loadWorkspace(true)}
              >
                <RecommendationSection recommendations={ws.recommendations} />
              </DashboardSectionErrorBoundary>
            </FadeUp>
          )}

          {ws?.forecasts && (
            <DashboardSectionErrorBoundary
              title="Predictive Forecasts"
              sectionKey="forecasts"
              onRetry={() => loadWorkspace(true)}
            >
              <Suspense fallback={<SectionSkeleton title="Predictive Forecasts" />}>
                <ForecastSection forecasts={ws.forecasts} />
              </Suspense>
            </DashboardSectionErrorBoundary>
          )}

          {ws?.scenarios && (
            <DashboardSectionErrorBoundary
              title="Scenario Simulations"
              sectionKey="scenarios"
              onRetry={() => loadWorkspace(true)}
            >
              <Suspense fallback={<SectionSkeleton title="Scenario Simulations" />}>
                <ScenarioSection scenarios={ws.scenarios} />
              </Suspense>
            </DashboardSectionErrorBoundary>
          )}

          {ws?.narratives && (
            <DashboardSectionErrorBoundary
              title="AI Executive Briefings"
              sectionKey="narratives"
              onRetry={() => loadWorkspace(true)}
            >
              <Suspense fallback={<SectionSkeleton title="Executive Briefings" />}>
                <NarrativeSection narratives={ws.narratives} />
              </Suspense>
            </DashboardSectionErrorBoundary>
          )}

          {ws?.insights && (
            <DashboardSectionErrorBoundary
              title="Strategic Insights & Themes"
              sectionKey="insights"
              onRetry={() => loadWorkspace(true)}
            >
              <Suspense fallback={<SectionSkeleton title="Strategic Insights" />}>
                <InsightSection insights={ws.insights} />
              </Suspense>
            </DashboardSectionErrorBoundary>
          )}

          {ws?.reports && (
            <DashboardSectionErrorBoundary
              title="Boardroom Reports & Exports"
              sectionKey="reports"
              onRetry={() => loadWorkspace(true)}
            >
              <Suspense fallback={<SectionSkeleton title="Boardroom Reports" />}>
                <ReportsSection
                  reportsSummary={ws.reports}
                  onOpenPreview={(id) => setPreviewReportId(id)}
                />
              </Suspense>
            </DashboardSectionErrorBoundary>
          )}

          {ws?.chat && (
            <DashboardSectionErrorBoundary
              title="AI Decision Copilot"
              sectionKey="chat"
              onRetry={() => loadWorkspace(true)}
            >
              <Suspense fallback={<SectionSkeleton title="AI Decision Copilot" />}>
                <ChatSection
                  datasetId={datasetId}
                  chatSummary={ws.chat}
                />
              </Suspense>
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
