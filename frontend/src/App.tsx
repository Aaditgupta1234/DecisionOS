import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './features/auth/AuthContext';
import { DatasetProvider } from './context/DatasetContext';
import { OrganizationProvider } from './context/OrganizationContext';
import { AppShell } from './components/layout/AppShell';
import { ProtectedRoute } from './features/auth/ProtectedRoute';
import { ErrorBoundary } from './shared/components/ErrorBoundary';

// Route Lazy Loading for Optimal Startup
const HomeView = React.lazy(() => import('./views/home/HomeView').then(m => ({ default: m.HomeView })));
const LoginPage = React.lazy(() => import('./features/auth/LoginPage'));
const DashboardView = React.lazy(() => import('./features/dashboard/DashboardView'));
const ExecutiveCommandCenterView = React.lazy(() => import('./features/workspace/ExecutiveCommandCenterView').then(m => ({ default: m.ExecutiveCommandCenterView })));
const MonitoringCenterView = React.lazy(() => import('./features/monitoring/MonitoringCenterView').then(m => ({ default: m.MonitoringCenterView })));
const SimulationStudioView = React.lazy(() => import('./features/simulation/SimulationStudioView').then(m => ({ default: m.SimulationStudioView })));
const KnowledgeGraphExplorerView = React.lazy(() => import('./features/knowledge-graph/KnowledgeGraphExplorerView').then(m => ({ default: m.KnowledgeGraphExplorerView })));
const AIAnalystWorkspaceView = React.lazy(() => import('./features/ai-analyst/AIAnalystWorkspaceView').then(m => ({ default: m.AIAnalystWorkspaceView })));
const DecisionCopilotView = React.lazy(() => import('./features/decision-copilot/DecisionCopilotView').then(m => ({ default: m.DecisionCopilotView })));
const ExecutiveReportsCenterView = React.lazy(() => import('./features/reports/ExecutiveReportsCenterView').then(m => ({ default: m.ExecutiveReportsCenterView })));
const DatasetsView = React.lazy(() => import('./features/datasets/DatasetsView'));
const SchemaMappingView = React.lazy(() => import('./features/datasets/SchemaMappingView'));
const MetricsView = React.lazy(() => import('./features/kpis/MetricsView'));
const DiagnosticsView = React.lazy(() => import('./features/diagnostics/DiagnosticsView'));
const RootCausesView = React.lazy(() => import('./features/root-causes/RootCausesView'));
const RecommendationsView = React.lazy(() => import('./features/recommendations/RecommendationsView'));
const ReportsView = React.lazy(() => import('./features/intelligence/ReportsView'));
const HistoryView = React.lazy(() => import('./features/history/AnalysisHistoryView'));
const AIInsightsView = React.lazy(() => import('./features/ai-insights/AIInsightsView'));
const ChatView = React.lazy(() => import('./features/chat-analyst/ChatView'));
const ExecutionCenterView = React.lazy(() => import('./features/execution/ExecutionCenterView'));
const InitiativeDetailsView = React.lazy(() => import('./features/initiatives/InitiativeDetailsView'));
const OutcomesView = React.lazy(() => import('./features/outcomes/OutcomesView'));
const OrganizationSettingsView = React.lazy(() => import('./views/settings/OrganizationSettingsView').then(m => ({ default: m.OrganizationSettingsView })));

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

export function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <OrganizationProvider>
            <DatasetProvider>
              <BrowserRouter>
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
                          <AppShell />
                        </ProtectedRoute>
                      }
                    >
                      <Route path="/dashboard" element={<ExecutiveCommandCenterView />} />
                      <Route path="/command-center" element={<ExecutiveCommandCenterView />} />
                      <Route path="/monitoring" element={<MonitoringCenterView />} />
                      <Route path="/simulations" element={<SimulationStudioView />} />
                      <Route path="/knowledge-graph" element={<KnowledgeGraphExplorerView />} />
                      <Route path="/ai-analyst" element={<AIAnalystWorkspaceView />} />
                      <Route path="/decision-copilot" element={<DecisionCopilotView />} />
                      <Route path="/datasets" element={<DatasetsView />} />
                      <Route path="/datasets/:id/mapping" element={<SchemaMappingView />} />
                      <Route path="/metrics" element={<MetricsView />} />
                      <Route path="/diagnostics" element={<DiagnosticsView />} />
                      <Route path="/root-causes" element={<RootCausesView />} />
                      <Route path="/recommendations" element={<RecommendationsView />} />
                      <Route path="/reports" element={<ExecutiveReportsCenterView />} />
                      <Route path="/history" element={<HistoryView />} />
                      <Route path="/ai-insights" element={<AIInsightsView />} />
                      <Route path="/chat" element={<ChatView />} />
                      <Route path="/execution" element={<ExecutionCenterView />} />
                      <Route path="/initiatives/:id" element={<InitiativeDetailsView />} />
                      <Route path="/outcomes" element={<OutcomesView />} />
                      <Route path="/settings/organization" element={<OrganizationSettingsView />} />
                      <Route path="*" element={<Navigate to="/command-center" replace />} />
                    </Route>
                  </Routes>
                </Suspense>
              </BrowserRouter>
            </DatasetProvider>
          </OrganizationProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
