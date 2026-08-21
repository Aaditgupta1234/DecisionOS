/**
 * Centralized React Query Key Factory for DecisionOS
 */

export const queryKeys = {
  health: ['backend', 'health'] as const,
  auth: {
    user: ['auth', 'user'] as const,
  },
  organizations: {
    all: ['organizations'] as const,
    current: ['organizations', 'current'] as const,
    detail: (id: string) => ['organizations', id] as const,
    members: (id: string) => ['organizations', id, 'members'] as const,
  },
  datasets: {
    all: (orgId?: string) => ['datasets', orgId || 'all'] as const,
    detail: (id: string) => ['datasets', id] as const,
    mapping: (id: string) => ['datasets', id, 'mapping'] as const,
  },
  metrics: {
    all: (datasetId: string) => ['datasets', datasetId, 'metrics'] as const,
    detail: (datasetId: string, metric: string) => ['datasets', datasetId, 'metrics', metric] as const,
  },
  diagnostics: {
    all: (datasetId: string) => ['datasets', datasetId, 'diagnostics'] as const,
  },
  rootCauses: {
    all: (datasetId: string) => ['datasets', datasetId, 'root-causes'] as const,
  },
  recommendations: {
    all: (datasetId: string) => ['datasets', datasetId, 'recommendations'] as const,
  },
  reports: {
    dataset: (datasetId: string) => ['datasets', datasetId, 'reports'] as const,
    executive: (datasetId: string) => ['datasets', datasetId, 'report'] as const,
    healthScore: (datasetId: string) => ['datasets', datasetId, 'health-score'] as const,
    executiveSummary: (datasetId: string) => ['datasets', datasetId, 'executive-summary'] as const,
  },
  history: {
    all: (datasetId?: string) => ['history', datasetId || 'all'] as const,
  },
  aiInsights: {
    all: (datasetId: string) => ['datasets', datasetId, 'ai-insights'] as const,
  },
  chat: {
    sessions: ['chat', 'sessions'] as const,
    messages: (sessionId: string) => ['chat', sessionId, 'messages'] as const,
  },
  strategy: {
    latest: (datasetId: string) => ['datasets', datasetId, 'strategy', 'latest'] as const,
  },
  knowledgeGraph: {
    dag: (datasetId: string) => ['datasets', datasetId, 'knowledge-graph', 'dag'] as const,
  },
  strategyExecution: {
    initiatives: (datasetId: string) => ['datasets', datasetId, 'strategy-execution', 'initiatives'] as const,
  },
  digitalTwin: {
    scenarios: (datasetId: string) => ['datasets', datasetId, 'digital-twin', 'scenarios'] as const,
    comparison: (datasetId: string) => ['datasets', datasetId, 'digital-twin', 'comparison'] as const,
  },
  governance: {
    scorecard: () => ['enterprise-os', 'governance', 'scorecard'] as const,
  },
  aiGovernance: {
    report: () => ['ai-governance', 'report'] as const,
    providers: () => ['ai', 'providers'] as const,
  },
  securityCenter: {
    posture: () => ['security-center', 'posture'] as const,
  },
  portfolio: {
    // Org-scoped — not dataset-scoped. Same cache entry shared by all three portfolio views.
    summary: () => ['portfolio', 'summary'] as const,
    riskSummary: () => ['portfolio', 'executive', 'risk'] as const,
  },
  competitiveIntelligence: {
    // Org-scoped. All three queries power CompetitiveIntelligenceCenterView.
    marketPosition: () => ['competitive-intelligence', 'market-position'] as const,
    comparisons: () => ['competitive-intelligence', 'comparisons'] as const,
    opportunities: () => ['competitive-intelligence', 'opportunities'] as const,
  },
};
