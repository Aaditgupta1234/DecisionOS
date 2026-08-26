import React from 'react';
import { ShieldAlert, AlertTriangle, Users, Globe, ArrowRight, WifiOff, Info, CheckCircle2, Shield, Layers } from 'lucide-react';
import { Card, Badge, MetricTile, Button } from '../../design-system';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { usePortfolioSummary, usePortfolioRisk } from '../../shared/hooks/usePortfolioSummary';
import type { WorkspacePortfolioEntry, RiskLevel, AssessmentState } from '../../types/portfolio';

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

function riskColor(level: RiskLevel, isAssessed: boolean): string {
  if (!isAssessed || level === 'NOT_ASSESSED' || level === 'INSUFFICIENT_DATA') return '#64748B';
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
  const summary = summaryQuery.data;
  const workspaces: WorkspacePortfolioEntry[] = summary?.workspaces ?? [];

  const workspaceCount = summary?.workspace_count ?? workspaces.length;
  const portfolioUnits = risk?.portfolio_size ?? workspaceCount;
  const rankedUnits = risk?.ranked_workspace_count ?? 0;

  // Explicit Assessment State Machine (Anti-Hallucination Governance)
  const assessmentState: AssessmentState = ((): AssessmentState => {
    if (workspaceCount === 0 || portfolioUnits === 0) return 'EMPTY_PORTFOLIO';
    if (rankedUnits === 0 || !summary?.benchmark_available) return 'INSUFFICIENT_DATA';
    return 'ASSESSMENT_AVAILABLE';
  })();

  const isAssessed = assessmentState === 'ASSESSMENT_AVAILABLE';

  // Surface highest-risk workspaces
  const riskWorkspaces = [...workspaces]
    .sort((a, b) => b.critical_finding_count - a.critical_finding_count)
    .slice(0, 5);

  const riskLevel: RiskLevel = isAssessed
    ? (risk?.risk_level ?? 'LOW')
    : assessmentState === 'EMPTY_PORTFOLIO'
      ? 'NOT_ASSESSED'
      : 'INSUFFICIENT_DATA';

  const riskLevelDisplay = isAssessed
    ? (risk?.risk_level ?? 'LOW')
    : assessmentState === 'EMPTY_PORTFOLIO'
      ? 'Not Assessed'
      : 'Insufficient Data';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: isAssessed ? '#EF4444' : '#64748B', fontWeight: 800 }}>
            Boardroom Risk Governance &amp; Exposure Radar
          </span>
          <span
            style={{
              fontSize: '0.65rem',
              fontWeight: 800,
              padding: '2px 8px',
              borderRadius: '12px',
              background: isAssessed ? 'rgba(239,68,68,0.15)' : 'rgba(100,116,139,0.15)',
              color: isAssessed ? '#EF4444' : '#94A3B8',
            }}
          >
            {isAssessed ? 'Active Assessment' : assessmentState === 'EMPTY_PORTFOLIO' ? 'Empty Portfolio' : 'Insufficient Telemetry'}
          </span>
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

      {/* Hero Metrics — Grounded in Deterministic Assessment State */}
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
              value={isAssessed && risk ? `${risk.risk_concentration_percent.toFixed(1)}%` : '—'}
              sublabel={isAssessed && risk ? `${risk.total_at_risk_workspaces} workspaces at risk` : 'No assessable units'}
              valueColor={riskColor(riskLevel, isAssessed)}
            />
            <MetricTile
              label="OVERALL RISK LEVEL"
              value={riskLevelDisplay}
              sublabel={isAssessed && risk ? `${risk.portfolio_size} total portfolio units` : 'Assessment unavailable'}
              valueColor={riskColor(riskLevel, isAssessed)}
            />
            <MetricTile
              label="CRITICAL WORKSPACES"
              value={isAssessed && risk ? String(risk.total_critical_workspaces) : '—'}
              sublabel={isAssessed ? 'Requiring immediate intervention' : 'No critical units identified'}
              valueColor={isAssessed ? '#EF4444' : '#64748B'}
            />
            <MetricTile
              label="RANKED COVERAGE"
              value={isAssessed && risk ? `${risk.ranked_workspace_count} / ${risk.portfolio_size}` : `${rankedUnits} / ${portfolioUnits}`}
              sublabel={isAssessed ? 'Workspaces with active benchmark rankings' : 'Benchmark coverage pending'}
              valueColor={isAssessed ? '#10B981' : '#64748B'}
            />
          </>
        )}
      </div>

      {/* Risk Concentration Matrix or Governance-Aware Empty Banner */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Portfolio Concentration Risk Matrix</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Boardroom Exposure Audit</span>
        </div>

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="72px" />)}
          </div>
        ) : !isAssessed || riskWorkspaces.length === 0 ? (
          /* Governance-Aware Empty State Banner */
          <div
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '12px',
              padding: '36px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              gap: '16px',
            }}
          >
            <ShieldAlert size={42} color="#64748B" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxWidth: '640px' }}>
              <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748B', fontWeight: 800 }}>
                Deterministic Governance Enforcement
              </span>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                Portfolio Risk Analytics Unavailable
              </h3>
              <p style={{ fontSize: '0.85rem', color: '#94A3B8', margin: '6px 0 0 0', lineHeight: 1.6 }}>
                Risk concentration analysis requires:
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginTop: '10px', textAlign: 'left' }}>
                <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                  • Active workspaces
                </div>
                <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                  • Portfolio governance telemetry
                </div>
                <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                  • Risk assessment inputs
                </div>
                <div style={{ padding: '10px 14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', fontSize: '0.78rem', color: '#CBD5E1' }}>
                  • Benchmark coverage data
                </div>
              </div>

              <div style={{ fontSize: '0.82rem', color: '#64748B', marginTop: '12px', fontStyle: 'italic', lineHeight: 1.5 }}>
                Current portfolio contains insufficient data to generate a concentration assessment.<br />
                <strong style={{ color: '#94A3B8' }}>No portfolio risk classification has been assigned.</strong>
              </div>
            </div>
          </div>
        ) : (
          /* Populated Risk Concentration Matrix */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {riskWorkspaces.map((w) => (
              <div
                key={w.workspace_id}
                style={{
                  background: 'rgba(15,23,42,0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '10px',
                  padding: '18px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '14px',
                }}
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
