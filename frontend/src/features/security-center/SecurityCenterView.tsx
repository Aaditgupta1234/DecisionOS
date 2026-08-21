import React from 'react';
import { ShieldCheck, CheckCircle2, Lock, FileText, AlertTriangle, Key, ShieldAlert, Layers, WifiOff } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../shared/api/queryKeys';
import { governanceApi } from '../../api';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { Card, Badge, MetricTile } from '../../design-system';
import type { SecurityPostureResponse, SecurityControl } from '../../types/governance';

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

export const SecurityCenterView: React.FC = () => {
  const { status, checkHealth } = useBackendHealth();
  const isOffline = status === 'offline';

  const postureQuery = useQuery({
    queryKey: queryKeys.securityCenter.posture(),
    queryFn: governanceApi.getSecurityPosture,
    enabled: status === 'connected',
    staleTime: 60000,
  });

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color="#F59E0B" />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: '#64748B' }}>Cannot load security posture data. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '8px', color: '#10B981', fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const posture: SecurityPostureResponse | undefined = postureQuery.data;
  const controls: SecurityControl[] = posture?.active_security_controls ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Enterprise Security Hardening &amp; Compliance
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Production Security &amp; SOC2 Compliance Center
        </h1>
      </div>

      {/* Error Banner */}
      {postureQuery.isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load security posture data.</strong>
          </div>
          <button onClick={() => postureQuery.refetch()} style={{ padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: '6px', color: '#FCA5A5', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}>
            Retry
          </button>
        </div>
      )}

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        {postureQuery.isLoading ? (
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
              label="OVERALL SECURITY SCORE"
              value={posture ? `${posture.overall_security_score} / 100` : '—'}
              sublabel={posture ? 'Grade A+ Certified' : 'Live security score'}
              valueColor="#10B981"
            />
            <MetricTile
              label="SOC2 TYPE II CONTROLS"
              value={posture?.soc2_type_ii_status ?? '—'}
              sublabel="Continuous Audit Verification"
              valueColor="#38BDF8"
            />
            <MetricTile
              label="THREAT EVENTS (PAST 24H)"
              value={posture ? `${posture.threat_events_past_24h} Incidents` : '—'}
              sublabel={posture ? `MFA Adoption: ${posture.mfa_adoption_rate}` : 'Live threat monitoring'}
              valueColor="#A855F7"
            />
            <MetricTile
              label="GDPR & ISO 27001 STATUS"
              value={posture?.gdpr_compliance_status ?? '—'}
              sublabel={posture ? `ISO 27001 Readiness: ${posture.iso_27001_readiness}` : 'Compliance status'}
              valueColor="#F59E0B"
            />
          </>
        )}
      </div>

      {/* Security Controls Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Active Enterprise Security Controls</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>SOC2 Type II Continuous Verification</span>
        </div>

        {postureQuery.isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[1, 2, 3, 4, 5].map((i) => <PulseSkeleton key={i} height="56px" />)}
          </div>
        ) : controls.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748B', fontSize: '0.9rem' }}>
            {postureQuery.isError ? 'Could not load security controls.' : 'No security controls available.'}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {controls.map((c, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <ShieldCheck size={16} color="#10B981" />
                    <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>{c.control}</span>
                  </div>
                  {c.framework && (
                    <div style={{ fontSize: '0.74rem', color: '#64748B', marginTop: '4px' }}>
                      Frameworks: {c.framework}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Badge variant="emerald" size="sm">
                    {c.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Audit Hash Footer */}
      {posture?.audit_hash && (
        <div style={{ background: 'rgba(15,23,42,0.4)', border: '1px solid #1E293B', borderRadius: '10px', padding: '12px 18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldCheck size={14} color="#10B981" />
          <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Audit Integrity Hash:</span>
          <code style={{ fontSize: '0.72rem', color: '#38BDF8', fontFamily: 'monospace' }}>{posture.audit_hash}</code>
        </div>
      )}
    </div>
  );
};
