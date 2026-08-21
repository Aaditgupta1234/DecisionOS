import React from 'react';
import { Bot, Sparkles, ShieldCheck, CheckCircle2, DollarSign, Clock, Layers, ArrowRight, WifiOff, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../shared/api/queryKeys';
import { governanceApi, DecisionApi } from '../../api';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { Card, Badge, MetricTile } from '../../design-system';
import type { AIGovernanceInteraction } from '../../types/governance';

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

export const AIGovernanceCenterView: React.FC = () => {
  const { status, checkHealth } = useBackendHealth();
  const isOffline = status === 'offline';

  const reportQuery = useQuery({
    queryKey: queryKeys.aiGovernance.report(),
    queryFn: governanceApi.getAIGovernanceReport,
    enabled: status === 'connected',
    staleTime: 60000,
  });

  const providersQuery = useQuery({
    queryKey: queryKeys.aiGovernance.providers(),
    queryFn: DecisionApi.listAIProviders,
    enabled: status === 'connected',
    staleTime: 60000,
  });

  // Combined loading to avoid partial rendering
  const isLoading = reportQuery.isLoading || providersQuery.isLoading;
  const isError = reportQuery.isError || providersQuery.isError;

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color="#F59E0B" />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Cannot load AI governance data. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '8px', color: '#A855F7', fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const report = reportQuery.data;
  const interactions: AIGovernanceInteraction[] = report?.recent_interactions ?? [];
  const providersData = providersQuery.data;
  const providers = (providersData as any)?.data?.providers ?? (providersData as any)?.providers ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
          AI Transparency, Safety &amp; Token Cost Governance
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          AI Usage &amp; Prompt Governance Center
        </h1>
      </div>

      {/* Error Banner */}
      {isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load AI governance data.</strong>
          </div>
          <button
            onClick={() => { reportQuery.refetch(); providersQuery.refetch(); }}
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
              label="TOTAL AUDITED AI PROMPTS"
              value={report ? report.total_ai_interactions.toLocaleString() : '—'}
              sublabel="Grounded in Evidence URNs"
              valueColor="#A855F7"
            />
            <MetricTile
              label="HALLUCINATION RATE"
              value={report?.hallucination_rate ?? '—'}
              sublabel="Zero Ungrounded Generative Output"
              valueColor="#10B981"
            />
            <MetricTile
              label="MONTHLY INFERENCE SPEND"
              value={report?.monthly_token_cost ?? '—'}
              sublabel={report ? `Avg latency: ${report.average_latency_ms}ms` : 'Live cost tracking'}
              valueColor="#38BDF8"
            />
            <MetricTile
              label="EXECUTIVE TRUST SCORE"
              value={report ? `${report.executive_trust_score} / 100` : '—'}
              sublabel="C-Suite Verified Confidence"
              valueColor="#F59E0B"
            />
          </>
        )}
      </div>

      {/* Active Providers */}
      {!isLoading && providers.length > 0 && (
        <Card style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>Active AI Provider Registry</span>
            {providersData && (
              <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
                Active: <strong style={{ color: '#10B981' }}>{(providersData as any)?.data?.active_provider ?? (providersData as any)?.active_provider}</strong>
                {' '}/ {(providersData as any)?.data?.active_model ?? (providersData as any)?.active_model}
              </span>
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {providers.map((p: any) => (
              <div
                key={p.name}
                style={{
                  background: 'rgba(15,23,42,0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '10px',
                }}
              >
                <div>
                  <div style={{ fontWeight: 800, color: '#FFFFFF', fontSize: '0.9rem' }}>{p.name}</div>
                  <div style={{ fontSize: '0.74rem', color: '#64748B', marginTop: '2px' }}>
                    {p.description} • Default model: <code style={{ color: '#38BDF8', fontFamily: 'monospace' }}>{p.default_model}</code>
                  </div>
                </div>
                <Badge variant={p.is_active ? 'emerald' : 'slate'} size="sm">
                  {p.is_active ? 'ACTIVE' : 'STANDBY'}
                </Badge>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Prompt Audit Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>AI Prompt &amp; Evidence Citation Ledger</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Deterministic Traceability</span>
        </div>

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2].map((i) => <PulseSkeleton key={i} height="80px" />)}
          </div>
        ) : interactions.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748B', fontSize: '0.9rem' }}>
            No AI interaction records available.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {interactions.map((a) => (
              <div
                key={a.id}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
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
                    <span style={{ fontSize: '0.96rem', fontWeight: 800, color: '#FFFFFF' }}>{a.query}</span>
                    <Badge variant="purple" size="sm">
                      {a.status}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '4px' }}>
                    User: <strong style={{ color: '#F1F5F9' }}>{a.user}</strong> • Model: {a.model} • Latency: {a.latency_ms}ms • Cost: <strong style={{ color: '#10B981' }}>{a.cost}</strong>
                  </div>
                  <div style={{ display: 'flex', gap: '6px', marginTop: '6px', flexWrap: 'wrap' }}>
                    {a.grounded_urns.map((u) => (
                      <span key={u} style={{ fontSize: '0.68rem', color: '#38BDF8', fontFamily: 'monospace', background: 'rgba(56,189,248,0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                        {u}
                      </span>
                    ))}
                  </div>
                </div>

                <span style={{ fontSize: '0.74rem', color: '#64748B' }}>{a.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
