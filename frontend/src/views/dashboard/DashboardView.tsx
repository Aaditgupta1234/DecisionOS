import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import {
  AIInsight,
  BusinessHealthResponse,
  DatasetMetric,
  ExecutiveSummaryResponse,
  IntelligenceReportResponse,
} from '../../types';
import { HealthScoreGauge } from '../../components/metrics/HealthScoreGauge';
import { MetricCard } from '../../components/metrics/MetricCard';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import {
  ShieldAlert,
  Sparkles,
  ArrowRight,
  TrendingUp,
  GitMerge,
  CheckCircle2,
  Database,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [report, setReport] = useState<IntelligenceReportResponse | null>(null);
  const [health, setHealth] = useState<BusinessHealthResponse | null>(null);
  const [executiveSummary, setExecutiveSummary] = useState<ExecutiveSummaryResponse | null>(null);
  const [aiInsight, setAiInsight] = useState<AIInsight | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch unified report, health score, and AI insight in parallel
      const [reportRes, healthRes, insightRes] = await Promise.allSettled([
        DecisionApi.getIntelligenceReport(datasetId),
        DecisionApi.getHealthScore(datasetId),
        DecisionApi.getLatestInsight(datasetId),
      ]);

      if (reportRes.status === 'fulfilled' && reportRes.value) {
        setReport(reportRes.value);
        setExecutiveSummary(reportRes.value.executive_summary);
      }

      if (healthRes.status === 'fulfilled' && healthRes.value) {
        setHealth(healthRes.value);
      }

      if (insightRes.status === 'fulfilled' && insightRes.value) {
        setAiInsight(insightRes.value);
      }
    } catch (err: any) {
      console.error('Error loading executive dashboard:', err);
      setError(err?.message || 'Failed to load executive dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchDashboardData(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Upload a CSV dataset or select an existing dataset from the top navigation to view the executive decision intelligence dashboard."
          icon={Database}
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="page-container">
        <h1 style={{ marginBottom: '24px' }}>Executive Briefing</h1>
        <LoadingSkeleton count={4} height="120px" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <ErrorBanner message={error} onRetry={() => fetchDashboardData(activeDataset.id)} />
      </div>
    );
  }

  const topMetrics = (report?.metrics || []).slice(0, 4);
  const topFinding = (report?.findings || [])[0];

  return (
    <div className="page-container">
      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-primary">Dataset: {activeDataset.name}</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Deterministic Intelligence & Executive Synthesis
            </span>
          </div>
          <h1>Executive Decision Briefing</h1>
        </div>
        <Link to="/chat" className="btn btn-ai">
          <Sparkles size={16} />
          <span>Ask AI Analyst</span>
        </Link>
      </div>

      {/* Top Section: Health Gauge + Executive Briefing Card */}
      <div className="grid-2" style={{ marginBottom: '24px' }}>
        {/* Business Health Card */}
        <div className="card-elevated" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Business Health Index
            </span>
            <div style={{ marginTop: '16px' }}>
              <HealthScoreGauge
                score={health?.score ?? report?.executive_summary.business_health_score ?? 0}
                status={health?.status ?? report?.executive_summary.business_health_status ?? 'HEALTHY'}
                description={health?.description || executiveSummary?.primary_issue}
              />
            </div>
          </div>

          <div
            style={{
              marginTop: '20px',
              paddingTop: '16px',
              borderTop: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.8rem',
            }}
          >
            <span style={{ color: 'var(--text-muted)' }}>Overall Confidence:</span>
            <span style={{ fontWeight: 600, color: 'var(--color-primary-light)' }}>
              {executiveSummary ? `${(executiveSummary.overall_confidence * 100).toFixed(0)}%` : '92%'}
            </span>
          </div>
        </div>

        {/* Executive Summary Narrative Card */}
        <div className="card-elevated" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Primary Risk & Causal Diagnosis
              </span>
              {executiveSummary?.severity && (
                <span className="badge badge-danger">{executiveSummary.severity}</span>
              )}
            </div>

            <h3 style={{ fontSize: '1.15rem', color: '#ffffff', marginBottom: '10px' }}>
              {executiveSummary?.primary_issue || 'Performance Diagnosis Active'}
            </h3>

            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '14px' }}>
              {executiveSummary?.expected_business_impact ||
                'Deterministic diagnostic rules have analyzed revenue, orders, and customer signals.'}
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {executiveSummary?.top_root_cause && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
                <GitMerge size={14} color="var(--color-warning)" />
                <span style={{ color: 'var(--text-muted)' }}>Root Cause:</span>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>
                  {executiveSummary.top_root_cause}
                </span>
              </div>
            )}

            {executiveSummary?.top_recommendation && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
                <CheckCircle2 size={14} color="var(--color-success)" />
                <span style={{ color: 'var(--text-muted)' }}>Top Action:</span>
                <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>
                  {executiveSummary.top_recommendation}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top 4 KPI Metrics Spotlight */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <h2>Core KPI Performance</h2>
          <Link to="/metrics" style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
            <span>View All Metrics</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {topMetrics.length > 0 ? (
          <div className="grid-4">
            {topMetrics.map((m) => (
              <MetricCard key={m.id || m.metric_key} metric={m} />
            ))}
          </div>
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
            No metrics computed for this dataset yet. Run calculations via Metrics tab.
          </div>
        )}
      </div>

      {/* AI Executive Insight Highlight (If Available) */}
      {aiInsight && (
        <div className="card card-ai" style={{ marginBottom: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-ai">✨ AI Executive Narrative</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-ai-light)' }}>
                Model: {aiInsight.model_name}
              </span>
            </div>
            <Link to="/ai-insights" className="btn btn-ghost btn-sm" style={{ color: 'var(--color-ai-light)' }}>
              <span>Full Narrative</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          <p style={{ fontSize: '0.95rem', color: 'var(--text-main)', lineHeight: 1.6, marginBottom: '16px' }}>
            {aiInsight.executive_narrative}
          </p>

          {aiInsight.key_takeaways && aiInsight.key_takeaways.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
              {aiInsight.key_takeaways.slice(0, 3).map((takeaway, idx) => (
                <div
                  key={idx}
                  style={{
                    backgroundColor: 'rgba(139, 92, 246, 0.08)',
                    border: '1px solid rgba(139, 92, 246, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '10px 14px',
                    fontSize: '0.825rem',
                    color: 'var(--text-main)',
                  }}
                >
                  • {takeaway}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Critical Finding Spotlight */}
      {topFinding && (
        <div className="card" style={{ borderLeft: '4px solid var(--color-danger)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldAlert size={16} color="var(--color-danger)" />
              <span style={{ fontWeight: 600, color: 'var(--color-danger)' }}>Top Diagnostic Finding</span>
            </div>
            <span className="badge badge-danger">{topFinding.severity}</span>
          </div>
          <h4 style={{ fontSize: '1rem', marginBottom: '6px' }}>{topFinding.title}</h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
            {topFinding.description}
          </p>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span style={{ color: 'var(--text-muted)' }}>Business Impact: {topFinding.business_impact}</span>
            <Link to="/diagnostics" style={{ color: 'var(--color-primary-light)', fontWeight: 500 }}>
              Investigate in Diagnostics →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};
