import React from 'react';
import { Globe, TrendingUp, TrendingDown, Minus, AlertTriangle, ArrowRight, ShieldCheck, Layers, Link2, WifiOff } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';
import { Link } from 'react-router-dom';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { usePortfolioSummary } from '../../shared/hooks/usePortfolioSummary';
import type { WorkspacePortfolioEntry, TrendDirection, PortfolioStatus } from '../../types/portfolio';

function PulseSkeleton({ width = '100%', height = '24px' }: { width?: string; height?: string }) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius: '6px',
        background: 'rgba(100,116,139,0.15)',
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  );
}

function TrendIcon({ direction }: { direction: TrendDirection }) {
  if (direction === 'UP') return <TrendingUp size={14} color="#10B981" />;
  if (direction === 'DOWN') return <TrendingDown size={14} color="#EF4444" />;
  return <Minus size={14} color="#64748B" />;
}

function statusVariant(status: PortfolioStatus): 'rose' | 'amber' | 'emerald' | 'slate' {
  if (status === 'CRITICAL') return 'rose';
  if (status === 'AT_RISK') return 'amber';
  if (status === 'HEALTHY') return 'emerald';
  return 'slate';
}

function healthColor(score: number): string {
  if (score >= 80) return '#10B981';
  if (score >= 65) return '#F59E0B';
  return '#EF4444';
}

function tierBadgeVariant(tier: string): 'purple' | 'emerald' | 'sky' | 'amber' {
  if (tier === 'LEADER') return 'purple';
  if (tier === 'STRONG') return 'emerald';
  if (tier === 'AVERAGE') return 'sky';
  return 'amber';
}

export const PortfolioRollupView: React.FC = () => {
  const { status, checkHealth } = useBackendHealth();
  const isOffline = status === 'offline';

  // Shared cache — same query key as CapitalAllocationStudioView, zero extra network calls
  const summaryQuery = usePortfolioSummary();

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color="#F59E0B" />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Cannot load portfolio rollup. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '8px', color: '#10B981', fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const summary = summaryQuery.data;
  const workspaces: WorkspacePortfolioEntry[] = summary?.workspaces ?? [];
  const criticalWorkspaces = workspaces.filter((w) => w.critical_finding_count > 0);
  const worstWorkspace = summary?.worst_workspace;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Enterprise Scale Hierarchy &amp; Drag Detection
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Multi-Portfolio Hierarchy &amp; Enterprise Rollup
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/capital-allocation" style={{ textDecoration: 'none' }}>
            <Button variant="primary" size="sm">
              Open Capital Allocation Studio →
            </Button>
          </Link>
        </div>
      </div>

      {/* Error Banner */}
      {summaryQuery.isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load portfolio rollup.</strong> The portfolio endpoint requires authentication.
          </div>
          <button onClick={() => summaryQuery.refetch()} style={{ padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: '6px', color: '#FCA5A5', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}>
            Retry
          </button>
        </div>
      )}

      {/* Hero Metric Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        {summaryQuery.isLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <div key={i} style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px' }}>
                <PulseSkeleton height="16px" width="60%" />
                <div style={{ marginTop: '8px' }}><PulseSkeleton height="40px" /></div>
                <div style={{ marginTop: '6px' }}><PulseSkeleton height="14px" width="80%" /></div>
              </div>
            ))}
          </>
        ) : (
          <>
            <MetricTile
              label="TOTAL WORKSPACES"
              value={summary ? String(summary.workspace_count) : '—'}
              sublabel={summary ? `${summary.analyzed_workspace_count} analyzed` : 'Org-level portfolio'}
              valueColor="#10B981"
            />
            <MetricTile
              label="PORTFOLIO COMPOSITE HEALTH"
              value={summary?.portfolio_health_score != null ? `${summary.portfolio_health_score.toFixed(1)} / 100` : '—'}
              sublabel={summary ? `Avg: ${summary.average_health_score?.toFixed(1) ?? '—'} across workspaces` : 'Live composite score'}
              valueColor="#38BDF8"
            />
            <MetricTile
              label="PRIMARY ATTENTION NEEDED"
              value={worstWorkspace?.workspace_name ?? 'None'}
              sublabel={worstWorkspace ? `Rank #${worstWorkspace.rank} • ${worstWorkspace.critical_finding_count} critical findings` : 'All workspaces healthy'}
              valueColor="#EF4444"
            />
            <MetricTile
              label="CRITICAL WORKSPACES"
              value={criticalWorkspaces.length > 0 ? `${criticalWorkspaces.length} Alerts` : 'None'}
              sublabel="Workspaces with active critical findings"
              valueColor="#A855F7"
            />
          </>
        )}
      </div>

      {/* Drag Alert Banner — only when worst workspace has critical findings */}
      {!summaryQuery.isLoading && worstWorkspace && worstWorkspace.critical_finding_count > 0 && (
        <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '12px', padding: '18px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <AlertTriangle size={20} color="#EF4444" />
            <div>
              <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>
                Portfolio Drag Detected: {worstWorkspace.workspace_name}
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                {worstWorkspace.critical_finding_count} critical finding{worstWorkspace.critical_finding_count !== 1 ? 's' : ''} • Rank #{worstWorkspace.rank} of {worstWorkspace.total_ranked} • Benchmark tier: {worstWorkspace.benchmark_tier}
              </div>
            </div>
          </div>
          <Link to="/diagnostics" style={{ textDecoration: 'none' }}>
            <Button variant="danger" size="sm">
              Investigate Root Causes →
            </Button>
          </Link>
        </div>
      )}

      {/* Workspace Hierarchy Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Global Workspace Portfolio Hierarchy</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
            {summary ? `${summary.portfolio_status} • Generated ${new Date(summary.generated_at).toLocaleDateString()}` : 'Multi-Tenant Hierarchy'}
          </span>
        </div>

        {summaryQuery.isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="72px" />)}
          </div>
        ) : workspaces.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#64748B' }}>
            No portfolio rollup data available.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {workspaces.map((w) => (
              <div
                key={w.workspace_id}
                style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid #1E293B', borderRadius: '10px', padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Globe size={16} color="#38BDF8" />
                    <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{w.workspace_name}</span>
                    <Badge variant={tierBadgeVariant(w.benchmark_tier)} size="sm">
                      {w.benchmark_tier}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                    Health: <strong style={{ color: healthColor(w.health_score) }}>{w.health_score.toFixed(1)}</strong> • Rank: #{w.rank}/{w.total_ranked} • {w.percentile.toFixed(0)}th percentile • Findings: {w.finding_count} ({w.critical_finding_count} critical)
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {w.critical_finding_count > 0 && (
                    <span style={{ fontSize: '0.74rem', color: '#EF4444', fontWeight: 800 }}>
                      ⚠ {w.critical_finding_count} CRITICAL
                    </span>
                  )}
                  <TrendIcon direction={w.trend_direction} />
                  <Link to="/portfolio" style={{ textDecoration: 'none' }}>
                    <Button variant="secondary" size="sm">
                      Open Scorecard →
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Portfolio Status Footer */}
      {summary && (
        <div style={{ background: 'rgba(15,23,42,0.4)', border: '1px solid #1E293B', borderRadius: '10px', padding: '12px 18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldCheck size={14} color="#10B981" />
          <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Portfolio Version:</span>
          <code style={{ fontSize: '0.72rem', color: '#38BDF8', fontFamily: 'monospace' }}>{summary.portfolio_version ?? '1.0'}</code>
          <span style={{ fontSize: '0.72rem', color: '#64748B', marginLeft: '12px' }}>Benchmark:</span>
          <span style={{ fontSize: '0.72rem', color: summary.benchmark_available ? '#10B981' : '#64748B', fontWeight: 700 }}>
            {summary.benchmark_available ? 'AVAILABLE' : 'NOT COMPUTED'}
          </span>
        </div>
      )}
    </div>
  );
};
