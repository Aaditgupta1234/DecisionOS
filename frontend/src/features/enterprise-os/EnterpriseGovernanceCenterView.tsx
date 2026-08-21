import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Lock,
  Plus,
  ArrowUpRight,
  TrendingUp,
  Sparkles,
  GitMerge,
  Scale,
  Award,
  RefreshCw,
  WifiOff,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../shared/api/queryKeys';
import { governanceApi } from '../../api';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import type { GovernanceDecision } from '../../types/governance';

const BRAND = {
  emerald: '#10B981',
  sky: '#38BDF8',
  purple: '#A855F7',
  amber: '#F59E0B',
  slate: '#64748B',
  white: '#FFFFFF',
  cardBg: '#090D14',
  border: '#1E293B',
};

const card = {
  background: BRAND.cardBg,
  border: `1px solid ${BRAND.border}`,
  borderRadius: '14px',
  padding: '20px',
  display: 'flex' as const,
  flexDirection: 'column' as const,
  gap: '6px',
};

const label = {
  fontSize: '0.72rem',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.06em',
  fontWeight: 800,
  color: BRAND.slate,
};

const bigValue = (color: string) => ({
  fontSize: '2.2rem',
  fontWeight: 900,
  color,
});

const sublabel = (color: string) => ({
  fontSize: '0.75rem',
  fontWeight: 700,
  color,
});

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

const statusColor = (status: string) => {
  if (status === 'IMPLEMENTED') return BRAND.emerald;
  if (status === 'APPROVED') return BRAND.sky;
  return BRAND.amber;
};

export const EnterpriseGovernanceCenterView: React.FC = () => {
  const [showSimModal, setShowSimModal] = useState(false);
  const { status, checkHealth } = useBackendHealth();
  const isOffline = status === 'offline';

  const scorecardQuery = useQuery({
    queryKey: queryKeys.governance.scorecard(),
    queryFn: governanceApi.getScorecard,
    enabled: status === 'connected',
    staleTime: 60000,
  });

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color={BRAND.amber} />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: BRAND.white }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: BRAND.slate }}>Cannot load governance scorecard. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.3)', borderRadius: '8px', color: BRAND.sky, fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const scorecard = scorecardQuery.data;
  const decisions: GovernanceDecision[] = scorecard?.decisions ?? [];

  const governanceHealth = scorecard?.governance_health_score ?? scorecard?.governance_health;
  const decisionEffectiveness = scorecard?.decision_effectiveness_pct ?? scorecard?.decision_effectiveness;
  const realizedValue = scorecard?.realized_decision_value;
  const boardCompliance = scorecard?.board_directive_compliance;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: BRAND.emerald, fontWeight: 800 }}>
            Decision Governance &amp; Compliance Engine
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: BRAND.white, margin: '4px 0 0 0' }}>
            Enterprise Decision Registry &amp; Governance Center
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {scorecardQuery.isFetching && (
            <div style={{ fontSize: '0.75rem', color: BRAND.slate, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} />
              Refreshing
            </div>
          )}
          <button
            onClick={() => setShowSimModal(true)}
            style={{
              padding: '8px 14px',
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: '8px',
              color: BRAND.sky,
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Sparkles size={14} />
            <span>Pre-Simulate Decision Impact</span>
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {scorecardQuery.isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load governance scorecard.</strong> The backend may require authentication or returned an error.
          </div>
          <button onClick={() => scorecardQuery.refetch()} style={{ padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: '6px', color: '#FCA5A5', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}>
            Retry
          </button>
        </div>
      )}

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={card}>
          <div style={label}>GOVERNANCE HEALTH</div>
          {scorecardQuery.isLoading
            ? <PulseSkeleton height="44px" />
            : <div style={bigValue(BRAND.emerald)}>{governanceHealth != null ? `${governanceHealth}%` : '—'}</div>
          }
          <div style={sublabel(BRAND.emerald)}>
            {scorecard ? `${scorecard.policy_rules_active ?? '—'} Policy Rules • ${scorecard.policy_violations ?? 0} Violations` : 'Live governance score'}
          </div>
        </div>

        <div style={card}>
          <div style={label}>DECISION EFFECTIVENESS</div>
          {scorecardQuery.isLoading
            ? <PulseSkeleton height="44px" />
            : <div style={bigValue(BRAND.sky)}>{decisionEffectiveness != null ? `${decisionEffectiveness}%` : '—'}</div>
          }
          <div style={sublabel('#94A3B8')}>Realized vs Approved ARR Outcome</div>
        </div>

        <div style={card}>
          <div style={label}>REALIZED DECISION VALUE</div>
          {scorecardQuery.isLoading
            ? <PulseSkeleton height="44px" />
            : <div style={bigValue(BRAND.purple)}>{realizedValue != null ? String(realizedValue) : '—'}</div>
          }
          <div style={sublabel(BRAND.purple)}>Actual ARR captured</div>
        </div>

        <div style={card}>
          <div style={label}>BOARD DIRECTIVES</div>
          {scorecardQuery.isLoading
            ? <PulseSkeleton height="44px" />
            : <div style={bigValue(BRAND.amber)}>{boardCompliance != null ? String(boardCompliance) : '—'}</div>
          }
          <div style={sublabel(BRAND.amber)}>Board alignment status</div>
        </div>
      </div>

      {/* Decision Registry Table */}
      <div style={{ background: BRAND.cardBg, border: `1px solid ${BRAND.border}`, borderRadius: '14px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: `1px solid ${BRAND.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: BRAND.white }}>Corporate Decision Registry</span>
          <span style={{ fontSize: '0.75rem', color: BRAND.slate }}>Permanent Institutional Audit Memory</span>
        </div>

        {scorecardQuery.isLoading ? (
          <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="60px" />)}
          </div>
        ) : decisions.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: BRAND.slate, fontSize: '0.9rem' }}>
            {scorecardQuery.isError ? 'Could not load governance records.' : 'No governance records available for this organization.'}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {decisions.map((dec) => (
              <div
                key={dec.code}
                style={{
                  padding: '20px',
                  borderBottom: `1px solid ${BRAND.border}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '14px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: 'rgba(16,185,129,0.15)', color: BRAND.emerald }}>
                      {dec.type}
                    </span>
                    <span style={{ fontSize: '0.95rem', fontWeight: 800, color: BRAND.white }}>
                      {dec.code}: {dec.title}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: BRAND.slate, marginTop: '4px' }}>
                    Owner: {dec.owner}
                    {dec.expected_value && <> • Expected: <strong style={{ color: BRAND.sky }}>{dec.expected_value}</strong></>}
                    {dec.realized_value && <> • Realized: <strong style={{ color: BRAND.emerald }}>{dec.realized_value}</strong></>}
                    {dec.accuracy && <> (Accuracy: {dec.accuracy})</>}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 800, color: statusColor(dec.status), background: `rgba(${dec.status === 'IMPLEMENTED' ? '16,185,129' : dec.status === 'APPROVED' ? '56,189,248' : '245,158,11'},0.1)`, padding: '4px 10px', borderRadius: '6px' }}>
                    {dec.status}
                  </span>
                  <span style={{ fontSize: '0.75rem', fontWeight: 800, color: BRAND.sky, background: 'rgba(56,189,248,0.1)', padding: '4px 10px', borderRadius: '6px' }}>
                    {dec.compliance}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Pre-Simulation Drawer Modal */}
      {showSimModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '20px',
          }}
          onClick={() => setShowSimModal(false)}
        >
          <div
            style={{
              backgroundColor: BRAND.cardBg,
              border: `1px solid ${BRAND.border}`,
              borderRadius: '16px',
              width: '100%',
              maxWidth: '620px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: '1.1rem', fontWeight: 800, color: BRAND.white }}>
              Governance Pre-Simulation Analysis
            </div>

            <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', padding: '14px', borderRadius: '8px', fontSize: '0.82rem', color: '#F1F5F9' }}>
              <strong style={{ color: BRAND.emerald }}>Governance Verdict: </strong>
              Pre-simulation requires an active decision selected from the registry above. Load a governance scorecard with active decisions to run impact analysis.
            </div>

            <button
              onClick={() => setShowSimModal(false)}
              style={{ padding: '10px', background: BRAND.sky, border: 'none', borderRadius: '8px', color: BRAND.cardBg, fontWeight: 800, cursor: 'pointer' }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
