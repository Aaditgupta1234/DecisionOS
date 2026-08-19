import React, { Suspense, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './features/auth/AuthContext';
import { DatasetProvider } from './context/DatasetContext';
import { OrganizationProvider } from './context/OrganizationContext';
import { AppShell } from './components/layout/AppShell';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { ErrorBoundary } from './shared/components/ErrorBoundary';
import { FrontendTelemetryProvider } from './components/observability/FrontendTelemetryProvider';
import { GlobalSearchModal } from './features/shared/GlobalSearchModal';
import { OnboardingWizardModal } from './features/shared/OnboardingWizardModal';
import { NotificationCenterDrawer } from './features/shared/NotificationCenterDrawer';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

// Landing Page & Auth
const HomeView = React.lazy(() => import('./views/home/HomeView').then(m => ({ default: m.HomeView })));
const LoginPage = React.lazy(() => import('./features/auth/LoginPage'));

// Core Multi-Portfolio & Executive Studios
const EnterpriseCommandCenterView = React.lazy(() => import('./features/enterprise-os/EnterpriseCommandCenterView').then(m => ({ default: m.EnterpriseCommandCenterView })));
const BoardroomCenterView = React.lazy(() => import('./features/boardroom/BoardroomCenterView').then(m => ({ default: m.BoardroomCenterView })));
const PortfolioRollupView = React.lazy(() => import('./features/portfolio-rollup/PortfolioRollupView').then(m => ({ default: m.PortfolioRollupView })));
const CapitalAllocationStudioView = React.lazy(() => import('./features/capital-allocation/CapitalAllocationStudioView').then(m => ({ default: m.CapitalAllocationStudioView })));
const KPIDictionaryView = React.lazy(() => import('./features/kpi-dictionary/KPIDictionaryView').then(m => ({ default: m.KPIDictionaryView })));
const RiskConcentrationRadarView = React.lazy(() => import('./features/risk-concentration/RiskConcentrationRadarView').then(m => ({ default: m.RiskConcentrationRadarView })));
const AutonomousAgentsHubView = React.lazy(() => import('./features/agents/AutonomousAgentsHubView').then(m => ({ default: m.AutonomousAgentsHubView })));

// Phase 8: Integrations, Data Governance, AI Audit & Production Operations
const IntegrationsCenterView = React.lazy(() => import('./features/integrations/IntegrationsCenterView').then(m => ({ default: m.IntegrationsCenterView })));
const EnterpriseDataReliabilityView = React.lazy(() => import('./features/enterprise-data/EnterpriseDataReliabilityView').then(m => ({ default: m.EnterpriseDataReliabilityView })));
const AIGovernanceCenterView = React.lazy(() => import('./features/ai-governance/AIGovernanceCenterView').then(m => ({ default: m.AIGovernanceCenterView })));
const ScheduledReportsView = React.lazy(() => import('./features/intelligence-delivery/ScheduledReportsView').then(m => ({ default: m.ScheduledReportsView })));
const ApiPlatformView = React.lazy(() => import('./features/api-platform/ApiPlatformView').then(m => ({ default: m.ApiPlatformView })));
const EnterpriseAdministrationView = React.lazy(() => import('./features/administration/EnterpriseAdministrationView').then(m => ({ default: m.EnterpriseAdministrationView })));
const SecurityCenterView = React.lazy(() => import('./features/security-center/SecurityCenterView').then(m => ({ default: m.SecurityCenterView })));
const PlatformOperationsView = React.lazy(() => import('./features/platform-ops/PlatformOperationsView').then(m => ({ default: m.PlatformOperationsView })));

// Phase 9: Launch Certification & Production Hardening
const ProductionCertificationCenterView = React.lazy(() => import('./features/production-readiness/ProductionCertificationCenterView').then(m => ({ default: m.ProductionCertificationCenterView })));

// Existing Core Intelligence Engines
const DatasetManagementCenterView = React.lazy(() => import('./features/data-management/DatasetManagementCenterView').then(m => ({ default: m.DatasetManagementCenterView })));
const JobCenterView = React.lazy(() => import('./features/jobs/JobCenterView').then(m => ({ default: m.JobCenterView })));
const SystemAdminCenterView = React.lazy(() => import('./features/admin/SystemAdminCenterView').then(m => ({ default: m.SystemAdminCenterView })));
const EnterpriseGovernanceCenterView = React.lazy(() => import('./features/enterprise-os/EnterpriseGovernanceCenterView').then(m => ({ default: m.EnterpriseGovernanceCenterView })));
const CompetitiveIntelligenceCenterView = React.lazy(() => import('./features/enterprise-os/CompetitiveIntelligenceCenterView').then(m => ({ default: m.CompetitiveIntelligenceCenterView })));
const EnterpriseOperatingSystemCenterView = React.lazy(() => import('./features/enterprise-os/EnterpriseOperatingSystemCenterView').then(m => ({ default: m.EnterpriseOperatingSystemCenterView })));
const EnterpriseOSHealthView = React.lazy(() => import('./features/enterprise-os/EnterpriseOSHealthView').then(m => ({ default: m.EnterpriseOSHealthView })));
const MonitoringCommandCenterView = React.lazy(() => import('./features/monitoring/MonitoringCommandCenterView').then(m => ({ default: m.MonitoringCommandCenterView })));
const StrategyExecutionCenterView = React.lazy(() => import('./features/strategy-execution/StrategyExecutionCenterView').then(m => ({ default: m.StrategyExecutionCenterView })));
const DigitalTwinWorkspaceView = React.lazy(() => import('./features/scenarios/DigitalTwinWorkspaceView').then(m => ({ default: m.DigitalTwinWorkspaceView })));
const KnowledgeGraphExplorerView = React.lazy(() => import('./features/knowledge-graph/KnowledgeGraphExplorerView').then(m => ({ default: m.KnowledgeGraphExplorerView })));
const DecisionCopilotView = React.lazy(() => import('./features/decision-copilot/DecisionCopilotView').then(m => ({ default: m.DecisionCopilotView })));
const ExecutiveReportsCenterView = React.lazy(() => import('./features/reports/ExecutiveReportsCenterView').then(m => ({ default: m.ExecutiveReportsCenterView })));
const MetricsView = React.lazy(() => import('./features/kpis/MetricsView'));
const DiagnosticsView = React.lazy(() => import('./features/diagnostics/DiagnosticsView'));
const RecommendationsView = React.lazy(() => import('./features/recommendations/RecommendationsView'));

import './styles/globals.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const RouteFallback = () => (
  <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ width: '28px', height: '28px', border: '3px solid #1E293B', borderTopColor: '#38BDF8', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
  </div>
);

function AppContent() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);

  useKeyboardShortcuts(() => setIsSearchOpen(true));

  return (
    <>
      <GlobalSearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
      <OnboardingWizardModal isOpen={isOnboardingOpen} onClose={() => setIsOnboardingOpen(false)} />
      <NotificationCenterDrawer isOpen={isNotificationOpen} onClose={() => setIsNotificationOpen(false)} />

      <Suspense fallback={<RouteFallback />}>
        <Routes>
          {/* Executive Marketing Landing Page */}
          <Route path="/" element={<HomeView />} />

          {/* Authentication Screen */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected In-App SaaS Routes */}
          <Route
            element={
              <ProtectedRoute>
                <AppShell
                  onOpenSearch={() => setIsSearchOpen(true)}
                  onOpenNotifications={() => setIsNotificationOpen(true)}
                  onOpenOnboarding={() => setIsOnboardingOpen(true)}
                />
              </ProtectedRoute>
            }
          >
            <Route path="/enterprise" element={<EnterpriseCommandCenterView />} />
            <Route path="/boardroom" element={<BoardroomCenterView />} />
            <Route path="/portfolio-rollup" element={<PortfolioRollupView />} />
            <Route path="/capital-allocation" element={<CapitalAllocationStudioView />} />
            <Route path="/kpi-dictionary" element={<KPIDictionaryView />} />
            <Route path="/risk-concentration" element={<RiskConcentrationRadarView />} />
            <Route path="/integrations" element={<IntegrationsCenterView />} />
            <Route path="/enterprise-data" element={<EnterpriseDataReliabilityView />} />
            <Route path="/ai-governance" element={<AIGovernanceCenterView />} />
            <Route path="/intelligence-delivery" element={<ScheduledReportsView />} />
            <Route path="/api-platform" element={<ApiPlatformView />} />
            <Route path="/administration" element={<EnterpriseAdministrationView />} />
            <Route path="/security-center" element={<SecurityCenterView />} />
            <Route path="/platform-ops" element={<PlatformOperationsView />} />
            <Route path="/production-readiness" element={<ProductionCertificationCenterView />} />
            <Route path="/agents" element={<AutonomousAgentsHubView />} />
            <Route path="/portfolio" element={<MetricsView />} />
            <Route path="/data-management" element={<DatasetManagementCenterView />} />
            <Route path="/diagnostics" element={<DiagnosticsView />} />
            <Route path="/recommendations" element={<RecommendationsView />} />
            <Route path="/decision-copilot" element={<DecisionCopilotView />} />
            <Route path="/knowledge-graph" element={<KnowledgeGraphExplorerView />} />
            <Route path="/reports" element={<ExecutiveReportsCenterView />} />
            <Route path="/digital-twin" element={<DigitalTwinWorkspaceView />} />
            <Route path="/strategy-execution" element={<StrategyExecutionCenterView />} />
            <Route path="/monitoring" element={<MonitoringCommandCenterView />} />
            <Route path="/governance" element={<EnterpriseGovernanceCenterView />} />
            <Route path="/competitive-intelligence" element={<CompetitiveIntelligenceCenterView />} />
            <Route path="/operating-system" element={<EnterpriseOperatingSystemCenterView />} />
            <Route path="/os-health" element={<EnterpriseOSHealthView />} />
            <Route path="/jobs" element={<JobCenterView />} />
            <Route path="/admin" element={<SystemAdminCenterView />} />

            {/* Aliases & Fallbacks */}
            <Route path="/command-center" element={<Navigate to="/enterprise" replace />} />
            <Route path="/dashboard" element={<Navigate to="/enterprise" replace />} />
            <Route path="/metrics" element={<Navigate to="/portfolio" replace />} />
            <Route path="/datasets" element={<Navigate to="/data-management" replace />} />
            <Route path="/tenant-admin" element={<Navigate to="/administration" replace />} />
            <Route path="/performance" element={<Navigate to="/production-readiness" replace />} />
            <Route path="/security-certification" element={<Navigate to="/production-readiness" replace />} />
            <Route path="/reliability" element={<Navigate to="/production-readiness" replace />} />
            <Route path="/backup-recovery" element={<Navigate to="/production-readiness" replace />} />
            <Route path="/resilience" element={<Navigate to="/production-readiness" replace />} />
            <Route path="/observability" element={<Navigate to="/production-readiness" replace />} />
            <Route path="/launch-certification" element={<Navigate to="/production-readiness" replace />} />
          </Route>
        </Routes>
      </Suspense>
    </>
  );
}

export function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <OrganizationProvider>
            <DatasetProvider>
              <BrowserRouter>
                <FrontendTelemetryProvider>
                  <AppContent />
                </FrontendTelemetryProvider>
              </BrowserRouter>
            </DatasetProvider>
          </OrganizationProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
