import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { OrganizationProvider } from './context/OrganizationContext';
import { DatasetProvider } from './context/DatasetContext';
import { AppShell } from './components/layout/AppShell';

import { DashboardView } from './views/dashboard/DashboardView';
import { MetricsView } from './views/metrics/MetricsView';
import { DiagnosticsView } from './views/diagnostics/DiagnosticsView';
import { RootCausesView } from './views/rootCauses/RootCausesView';
import { RecommendationsView } from './views/recommendations/RecommendationsView';
import { AIInsightsView } from './views/aiInsights/AIInsightsView';
import { StrategyPlannerView } from './views/strategy/StrategyPlannerView';
import { ScenariosView } from './views/scenarios/ScenariosView';
import { ForecastsView } from './views/forecasts/ForecastsView';
import { ChatView } from './views/chat/ChatView';
import { ReportsView } from './views/reports/ReportsView';
import { OrganizationSettingsView } from './views/settings/OrganizationSettingsView';
import { DatasetsView } from './views/datasets/DatasetsView';
import { HomeView } from './views/home/HomeView';

import './styles/globals.css';

export function App() {
  return (
    <AuthProvider>
      <OrganizationProvider>
        <DatasetProvider>
          <BrowserRouter>
            <Routes>
              {/* Executive Landing Page & Command Center Showcase */}
              <Route path="/" element={<HomeView />} />

              {/* In-App Command Center Views */}
              <Route element={<AppShell />}>
                <Route path="/dashboard" element={<DashboardView />} />
                <Route path="/metrics" element={<MetricsView />} />
                <Route path="/diagnostics" element={<DiagnosticsView />} />
                <Route path="/root-causes" element={<RootCausesView />} />
                <Route path="/recommendations" element={<RecommendationsView />} />
                <Route path="/ai-insights" element={<AIInsightsView />} />
                <Route path="/strategy" element={<StrategyPlannerView />} />
                <Route path="/scenarios" element={<ScenariosView />} />
                <Route path="/forecasts" element={<ForecastsView />} />
                <Route path="/chat" element={<ChatView />} />
                <Route path="/reports" element={<ReportsView />} />
                <Route path="/settings/organization" element={<OrganizationSettingsView />} />
                <Route path="/datasets" element={<DatasetsView />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </DatasetProvider>
      </OrganizationProvider>
    </AuthProvider>
  );
}

export default App;
