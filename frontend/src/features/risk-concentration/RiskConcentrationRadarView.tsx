import React from 'react';
import { ShieldAlert, AlertTriangle, Users, Globe, ArrowRight, WifiOff } from 'lucide-react';
import { Card, Badge, MetricTile, Button } from '../../design-system';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { usePortfolioSummary, usePortfolioRisk } from '../../shared/hooks/usePortfolioSummary';
import type { WorkspacePortfolioEntry, RiskLevel } from '../../types/portfolio';

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

function riskBadgeVariant(level: RiskLevel): 'rose' | 'amber' | 'emerald' | 'sky' {
  if (level === 'CRITICAL') return 'rose';
  if (level === 'HIGH') return 'amber';
  if (level === 'MODERATE') return 'sky';
  return 'emerald';
}

function riskColor(level: RiskLevel): string {
  if (level === 'CRITICAL') return '#EF4444';
  if (level === 'HIGH') return '#F59E0B';
  if (level === 'MODERATE') return '#38BDF8';
  return '#10B981';
}

export const RiskConcentrationRadarView: React.FC = () => {
  const { status, checkHealth } = useBackendHealth();
  const isOffline = status === 'offline';

  // Both queries share their cache with CapitalAllocationStudioView + PortfolioRollupView
  const riskQuery = usePortfolioRisk();
  const summaryQuery = usePortfolioSummary();

  const isLoading = riskQuery.isLoading || summaryQuery.isLoading;
  const isError = riskQuery.isError || summaryQuery.isError;

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color="#F59E0B" />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Cannot load risk concentration data. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', color: '#EF4444', fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const risk = riskQuery.data;
  const workspaces: WorkspacePortfolioEntry[] = summaryQuery.data?.workspaces ?? [];
  // Surface the highest-risk workspaces (most critical findings, sorted descending)
  const riskWorkspaces = [...workspaces]
    .sort((a, b) => b.critical_finding_count - a.critical_finding_count)
    .slice(0, 5);

  const riskLevel: RiskLevel = risk?.risk_level ?? 'LOW';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#EF4444', fontWeight: 800 }}>
          Boardroom Risk Governance &amp; Exposure Radar
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Enterprise Revenue &amp; Portfolio Concentration Radar
        </h1>
      </div>

      {/* Error Banner */}
      {isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load portfolio risk data.</strong>
          </div>
          <button
            onClick={() => { riskQuery.refetch(); summaryQuery.refetch(); }}
            style={{ padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: '6px', color: '#FCA5A5', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        {isLoading ? (
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
              label="RISK CONCENTRATION"
              value={risk ? `${risk.risk_concentration_percent.toFixed(1)}%` : '—'}
              sublabel={risk ? `${risk.total_at_risk_workspaces} workspaces at risk` : 'Live risk tracking'}
              valueColor={riskColor(riskLevel)}
            />
            <MetricTile
              label="OVERALL RISK LEVEL"
              value={risk?.risk_level ?? '—'}
              sublabel={risk ? `${risk.portfolio_size} total portfolio units` : 'Portfolio risk grade'}
              valueColor={riskColor(riskLevel)}
            />
            <MetricTile
              label="CRITICAL WORKSPACES"
              value={risk ? String(risk.total_critical_workspaces) : '—'}
              sublabel="Requiring immediate intervention"
              valueColor="#EF4444"
            />
            <MetricTile
              label="RANKED COVERAGE"
              value={risk ? `${risk.ranked_workspace_count} / ${risk.portfolio_size}` : '—'}
              sublabel="Workspaces with active benchmark rankings"
              valueColor="#10B981"
            />
          </>
        )}
      </div>

      {/* Top Risk Concentration Matrix */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Portfolio Concentration Risk Matrix</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Boardroom Exposure Audit</span>
        </div>

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="72px" />)}
          </div>
        ) : riskWorkspaces.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#64748B' }}>
            No risk concentration data available for this portfolio.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {riskWorkspaces.map((w) => (
              <div
                key={w.workspace_id}
                style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid #1E293B', borderRadius: '10px', padding: '18px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{w.workspace_name}</span>
                    <Badge
                      variant={w.critical_finding_count > 0 ? 'rose' : 'amber'}
                      size="sm"
                    >
                      {w.critical_finding_count > 0 ? 'CRITICAL_CONCENTRATION' : 'HIGH_CONCENTRATION'}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                    Health: <strong style={{ color: w.health_score < 75 ? '#EF4444' : '#10B981' }}>{w.health_score.toFixed(1)}</strong> • Rank: <strong>#{w.rank}</strong> • Critical Findings: <strong style={{ color: '#EF4444' }}>{w.critical_finding_count}</strong> • Total Findings: {w.finding_count}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Button variant="danger" size="sm">
                    Deploy Retention Playbook
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
