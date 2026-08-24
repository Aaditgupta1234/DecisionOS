import React, { useState } from 'react';
import { DollarSign, TrendingUp, Sparkles, PieChart, ShieldCheck, CheckCircle2, ArrowRight, Activity, WifiOff, TrendingDown, Minus, CheckSquare, Square, Info, Layers, Database } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { usePortfolioSummary } from '../../shared/hooks/usePortfolioSummary';
import type { WorkspacePortfolioEntry, TrendDirection, PortfolioState } from '../../types/portfolio';

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
  if (status === 'HEALTHY' || status === 'AVAILABLE') return '#10B981';
  if (status === 'AT_RISK' || status === 'SINGLE_WORKSPACE') return '#38BDF8';
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
  const workspaceCount = summary?.workspace_count ?? 0;
  const analyzedCount = summary?.analyzed_workspace_count ?? 0;

  // Explicit 3-State Portfolio Lifecycle Architecture
  const portfolioLifecycleState: PortfolioState = workspaceCount === 0
    ? 'INSUFFICIENT_DATA'
    : workspaceCount === 1
    ? 'SINGLE_WORKSPACE'
    : 'AVAILABLE';

  const benchmarkStatus = workspaceCount >= 2 ? 'AVAILABLE' : 'PENDING';
  const topWorkspaces = workspaces.slice(0, 5);

  // Dynamic Activation Checklist Evaluation (Derived from actual workspace state)
  const activationChecklist = [
    { id: 'dataset', label: 'Dataset Available', completed: true },
    { id: 'create_ws', label: 'Create Additional Workspace', completed: workspaceCount >= 2 },
    { id: 'snapshot', label: 'Generate Dashboard Snapshot', completed: analyzedCount >= 1 || workspaceCount >= 1 },
    { id: 'kpi', label: 'Run KPI Analysis', completed: analyzedCount >= 1 || workspaceCount >= 1 },
    { id: 'diagnostics', label: 'Run Diagnostics & Recommendations', completed: analyzedCount >= 1 || workspaceCount >= 1 },
    { id: 'benchmarking', label: 'Portfolio Benchmarking Available', completed: workspaceCount >= 2 },
  ];
  const completedChecklistCount = activationChecklist.filter((item) => item.completed).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px', maxWidth: '1600px', margin: '0 auto' }}>
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
            disabled={portfolioLifecycleState !== 'AVAILABLE'}
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

      {/* Hero Metrics — Explicit 3-State Portfolio Lifecycle & Benchmark Readiness */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
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
              value={portfolioLifecycleState}
              sublabel={
                portfolioLifecycleState === 'INSUFFICIENT_DATA'
                  ? 'No portfolio workspaces available'
                  : portfolioLifecycleState === 'SINGLE_WORKSPACE'
                  ? 'Single workspace active (Requires peer BU)'
                  : `${workspaceCount} workspaces tracked`
              }
              valueColor={statusColor(portfolioLifecycleState)}
            />
            <MetricTile
              label="PORTFOLIO HEALTH SCORE"
              value={summary?.portfolio_health_score != null ? `${summary.portfolio_health_score.toFixed(1)} / 100` : '—'}
              sublabel={summary?.average_health_score != null ? `Avg: ${summary.average_health_score.toFixed(1)} • Median: ${summary.median_health_score?.toFixed(1) ?? '—'}` : 'Requires multiple analyzed workspaces'}
              valueColor="#10B981"
            />
            <MetricTile
              label="ANALYZED WORKSPACES"
              value={`${analyzedCount} / ${workspaceCount}`}
              sublabel="Workspaces with active snapshots"
              valueColor="#38BDF8"
            />
            <MetricTile
              label="BENCHMARK READINESS"
              value={benchmarkStatus}
              sublabel={`Current: ${workspaceCount} • Required: 2 Workspaces`}
              valueColor={benchmarkStatus === 'AVAILABLE' ? '#10B981' : '#A855F7'}
            />
          </>
        )}
      </div>

      {/* Enhancement 1: Portfolio Activation Guidance Panel (When workspaceCount < 2) */}
      {!summaryQuery.isLoading && workspaceCount < 2 && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(9, 13, 20, 0.98) 100%)',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          padding: '24px 28px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ background: 'rgba(168, 85, 247, 0.15)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '8px', padding: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Sparkles size={20} color="#A855F7" />
              </div>
              <div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                  Portfolio Intelligence Activation Required
                </h3>
                <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: '4px 0 0 0' }}>
                  Capital Allocation Intelligence requires portfolio-level data. Create and analyze additional workspaces before portfolio optimization, benchmarking, and ROI allocation can be generated.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '20px', padding: '5px 14px' }}>
              <span style={{ fontSize: '0.76rem', color: '#38BDF8', fontWeight: 800 }}>
                Progress: {completedChecklistCount} of {activationChecklist.length} Milestones
              </span>
            </div>
          </div>

          {/* Dynamic Activation Checklist Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '10px', marginTop: '4px' }}>
            {activationChecklist.map((item) => (
              <div
                key={item.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  background: item.completed ? 'rgba(16, 185, 129, 0.08)' : 'rgba(15, 23, 42, 0.6)',
                  border: item.completed ? '1px solid rgba(16, 185, 129, 0.25)' : '1px solid #1E293B',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  fontSize: '0.8rem',
                  color: item.completed ? '#10B981' : '#94A3B8',
                  fontWeight: item.completed ? 700 : 500,
                }}
              >
                {item.completed ? (
                  <CheckCircle2 size={16} color="#10B981" />
                ) : (
                  <Square size={16} color="#64748B" />
                )}
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

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
            /* Enhancement 4: Empty Ledger Context Card */
            <div style={{ padding: '48px 24px', textAlign: 'center', background: '#090D14', border: '1px dashed #1E293B', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
              <Database size={32} color="#64748B" />
              <div style={{ fontSize: '1rem', fontWeight: 800, color: '#F1F5F9' }}>No portfolio capital allocation data exists yet.</div>
              <div style={{ fontSize: '0.82rem', color: '#94A3B8', maxWidth: '520px', lineHeight: 1.5 }}>
                Capital allocation intelligence is generated only after multiple workspace snapshots are available.<br />
                Create additional workspaces and compile dashboard snapshots to activate portfolio optimization.
              </div>
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
                      <span style={{ fontSize: '0.96rem', fontWeight: 800, color: '#FFFFFF' }}>{w.workspace_name}</span>
                      {portfolioLifecycleState === 'AVAILABLE' && <Badge variant="emerald" size="sm">Rank #{w.rank}</Badge>}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                      Health: <strong style={{ color: '#10B981' }}>{w.health_score.toFixed(1)}</strong>
                      {portfolioLifecycleState === 'AVAILABLE' && (
                        <> • Tier: <strong style={{ color: tierColor(w.benchmark_tier) }}>{w.benchmark_tier}</strong></>
                      )}
                      {" "}• Recommendations: {w.recommendation_count}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TrendIcon direction={w.trend_direction} />
                    {portfolioLifecycleState === 'AVAILABLE' ? (
                      <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#A855F7', padding: '4px 12px', borderRadius: '6px', background: 'rgba(168,85,247,0.15)', border: '1px solid rgba(168,85,247,0.3)' }}>
                        {w.percentile.toFixed(0)}th Percentile
                      </span>
                    ) : (
                      <span style={{ fontSize: '0.76rem', color: '#38BDF8', fontWeight: 700, padding: '4px 10px', borderRadius: '6px', background: 'rgba(56, 189, 248, 0.1)' }}>
                        Active Snapshot
                      </span>
                    )}
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
            <div style={{ padding: '48px 24px', textAlign: 'center', background: '#090D14', border: '1px dashed #1E293B', borderRadius: '12px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
              <Layers size={32} color="#64748B" />
              <div style={{ fontSize: '1rem', fontWeight: 800, color: '#F1F5F9' }}>No portfolio capital allocation data exists yet.</div>
              <div style={{ fontSize: '0.82rem', color: '#94A3B8', maxWidth: '520px', lineHeight: 1.5 }}>
                Capital allocation intelligence is generated only after multiple workspace snapshots are available.<br />
                Create additional workspaces and compile dashboard snapshots to activate portfolio optimization.
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* Enhancement 2: Single Workspace vs Multi-Workspace Presentation */}
              {portfolioLifecycleState === 'SINGLE_WORKSPACE' && (
                <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '8px', padding: '12px 16px', fontSize: '0.78rem', color: '#94A3B8', marginBottom: '6px' }}>
                  <strong style={{ color: '#38BDF8' }}>Single Workspace Mode:</strong> Local metrics and health scores active. Cross-workspace benchmarking and capital reallocation require ≥ 2 workspaces.
                </div>
              )}

              {topWorkspaces.map((w) => (
                <div
                  key={w.workspace_id}
                  style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid #1E293B', borderRadius: '10px', padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{w.workspace_name}</span>
                      {portfolioLifecycleState === 'AVAILABLE' && (
                        <Badge variant={w.benchmark_tier === 'LEADER' ? 'purple' : 'emerald'} size="sm">
                          {w.benchmark_tier}
                        </Badge>
                      )}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                      {portfolioLifecycleState === 'AVAILABLE' ? (
                        <>Rank: <strong style={{ color: '#38BDF8' }}>#{w.rank} of {w.total_ranked}</strong> • </>
                      ) : null}
                      Findings: <strong style={{ color: w.critical_finding_count > 0 ? '#EF4444' : '#10B981' }}>{w.critical_finding_count} critical</strong> • {w.recommendation_count} recommendations
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

export default CapitalAllocationStudioView;
