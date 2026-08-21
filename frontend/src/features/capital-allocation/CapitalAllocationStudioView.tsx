import React, { useState } from 'react';
import { DollarSign, TrendingUp, Sparkles, PieChart, ShieldCheck, CheckCircle2, ArrowRight, Activity, WifiOff, TrendingDown, Minus } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { usePortfolioSummary } from '../../shared/hooks/usePortfolioSummary';
import type { WorkspacePortfolioEntry, TrendDirection } from '../../types/portfolio';

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

function tierColor(tier: string): string {
  if (tier === 'LEADER') return '#A855F7';
  if (tier === 'STRONG') return '#10B981';
  if (tier === 'AVERAGE') return '#38BDF8';
  return '#F59E0B';
}

function statusColor(status: string): string {
  if (status === 'HEALTHY') return '#10B981';
  if (status === 'AT_RISK') return '#F59E0B';
  if (status === 'CRITICAL') return '#EF4444';
  return '#64748B';
}

export const CapitalAllocationStudioView: React.FC = () => {
  const [strategyExecuted, setStrategyExecuted] = useState(false);
  const [activeTab, setActiveTab] = useState<'OPTIMIZATION' | 'REALIZED_OUTCOMES'>('OPTIMIZATION');

  const { status, checkHealth } = useBackendHealth();
  const summaryQuery = usePortfolioSummary();
  const isOffline = status === 'offline';

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color="#F59E0B" />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Cannot load portfolio intelligence. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '8px', color: '#A855F7', fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const summary = summaryQuery.data;
  const workspaces: WorkspacePortfolioEntry[] = summary?.workspaces ?? [];
  const topWorkspaces = workspaces.slice(0, 5);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
            Enterprise Capital Deployment &amp; ROI Optimization
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Capital Allocation Intelligence Studio
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', padding: '3px' }}>
            <button
              onClick={() => setActiveTab('OPTIMIZATION')}
              style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', background: activeTab === 'OPTIMIZATION' ? '#38BDF8' : 'transparent', color: activeTab === 'OPTIMIZATION' ? '#090D14' : '#94A3B8', fontWeight: 700, fontSize: '0.76rem', cursor: 'pointer' }}
            >
              Workspace Rankings
            </button>
            <button
              onClick={() => setActiveTab('REALIZED_OUTCOMES')}
              style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', background: activeTab === 'REALIZED_OUTCOMES' ? '#10B981' : 'transparent', color: activeTab === 'REALIZED_OUTCOMES' ? '#090D14' : '#94A3B8', fontWeight: 700, fontSize: '0.76rem', cursor: 'pointer' }}
            >
              Outcome Attribution
            </button>
          </div>

          <Button
            variant="primary"
            size="sm"
            icon={<Sparkles size={14} />}
            onClick={() => setStrategyExecuted(true)}
          >
            Execute Allocation Strategy
          </Button>
        </div>
      </div>

      {/* Error Banner */}
      {summaryQuery.isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load portfolio data.</strong> The portfolio endpoint requires authentication.
          </div>
          <button onClick={() => summaryQuery.refetch()} style={{ padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: '6px', color: '#FCA5A5', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}>
            Retry
          </button>
        </div>
      )}

      {/* Hero Metrics */}
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
              label="PORTFOLIO STATUS"
              value={summary?.portfolio_status ?? '—'}
              sublabel={summary ? `${summary.workspace_count} workspaces tracked` : 'Org-level portfolio'}
              valueColor={statusColor(summary?.portfolio_status ?? '')}
            />
            <MetricTile
              label="PORTFOLIO HEALTH SCORE"
              value={summary?.portfolio_health_score != null ? `${summary.portfolio_health_score.toFixed(1)} / 100` : '—'}
              sublabel={summary ? `Avg: ${summary.average_health_score?.toFixed(1) ?? '—'} • Median: ${summary.median_health_score?.toFixed(1) ?? '—'}` : 'Live health tracking'}
              valueColor="#10B981"
            />
            <MetricTile
              label="ANALYZED WORKSPACES"
              value={summary ? `${summary.analyzed_workspace_count} / ${summary.workspace_count}` : '—'}
              sublabel="Workspaces with active snapshots"
              valueColor="#38BDF8"
            />
            <MetricTile
              label="BENCHMARK STATUS"
              value={summary?.benchmark_available ? 'AVAILABLE' : 'PENDING'}
              sublabel={summary?.best_workspace ? `Leader: ${summary.best_workspace.workspace_name}` : 'Benchmarks not yet computed'}
              valueColor="#A855F7"
            />
          </>
        )}
      </div>

      {/* Allocation Table / Outcome Attribution */}
      {activeTab === 'REALIZED_OUTCOMES' ? (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Workspace Outcome Attribution</span>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Closed-Loop Portfolio ROI</span>
          </div>

          {summaryQuery.isLoading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="70px" />)}
            </div>
          ) : workspaces.length === 0 ? (
            <div style={{ padding: '32px', textAlign: 'center', color: '#64748B' }}>No portfolio data available.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {workspaces.map((w) => (
                <div
                  key={w.workspace_id}
                  style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid #1E293B', borderRadius: '10px', padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.96rem', fontWeight: 800, color: '#FFFFFF' }}>{w.workspace_name}</span>
                      <Badge variant="emerald" size="sm">Rank #{w.rank}</Badge>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                      Health: <strong style={{ color: '#10B981' }}>{w.health_score.toFixed(1)}</strong> • Tier: <strong style={{ color: tierColor(w.benchmark_tier) }}>{w.benchmark_tier}</strong> • Recommendations: {w.recommendation_count}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TrendIcon direction={w.trend_direction} />
                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#A855F7', padding: '4px 12px', borderRadius: '6px', background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.3)' }}>
                      {w.percentile.toFixed(0)}th Percentile
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      ) : (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Workspace Capital Allocation Ledger</span>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Portfolio Elasticity Optimization</span>
          </div>

          {summaryQuery.isLoading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="70px" />)}
            </div>
          ) : topWorkspaces.length === 0 ? (
            <div style={{ padding: '32px', textAlign: 'center', color: '#64748B' }}>No capital allocation data available for this portfolio.</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {topWorkspaces.map((w) => (
                <div
                  key={w.workspace_id}
                  style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid #1E293B', borderRadius: '10px', padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{w.workspace_name}</span>
                      <Badge variant={w.benchmark_tier === 'LEADER' ? 'purple' : 'emerald'} size="sm">
                        {w.benchmark_tier}
                      </Badge>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                      Rank: <strong style={{ color: '#38BDF8' }}>#{w.rank} of {w.total_ranked}</strong> • Findings: <strong style={{ color: w.critical_finding_count > 0 ? '#EF4444' : '#10B981' }}>{w.critical_finding_count} critical</strong> • {w.recommendation_count} recommendations
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TrendIcon direction={w.trend_direction} />
                    <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#FFFFFF', padding: '4px 12px', borderRadius: '6px', background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.3)' }}>
                      {w.health_score.toFixed(1)} / 100
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {strategyExecuted && !summaryQuery.isLoading && (
            <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', padding: '16px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle2 size={18} color="#10B981" />
                <span style={{ fontSize: '0.84rem', color: '#F1F5F9' }}>
                  Capital allocation strategy dispatched to Governance Decision Registry for <strong>{summary?.workspace_count ?? 0} workspaces</strong>.
                </span>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};
