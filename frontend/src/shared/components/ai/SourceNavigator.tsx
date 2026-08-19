import React from 'react';
import { Activity, AlertTriangle, GitMerge, Zap, ArrowRight, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  metrics?: { label: string; key: string }[];
  findings?: { label: string; id: string }[];
  rootCauses?: { label: string; id: string }[];
  recommendations?: { label: string; id: string }[];
}

export const SourceNavigator: React.FC<Props> = ({
  metrics = [
    { label: 'Revenue ($4.2M)', key: 'revenue' },
    { label: 'Retention Rate (85.8%)', key: 'retention_rate' },
  ],
  findings = [
    { label: 'SE Logistics Deterioration', id: 'f-1' },
    { label: 'Secondary Hub Bottleneck', id: 'f-2' },
  ],
  rootCauses = [
    { label: 'Courier SLA Delays (48% weight)', id: 'rc_1' },
  ],
  recommendations = [
    { label: 'Targeted Win-Back Campaign (+$180K)', id: 'rec_1' },
  ],
}) => {
  return (
    <div style={{
      background: '#070A0F',
      border: '1px solid #141C28',
      borderRadius: '8px',
      padding: '12px 14px',
      marginTop: '12px',
    }}>
      <div style={{ fontSize: '10.5px', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
        Interactive Source Navigator (Click to Inspect Grounding Telemetry):
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {/* Metric Links */}
        {metrics.map((m) => (
          <Link
            key={m.key}
            to="/metrics"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              background: 'rgba(56, 189, 248, 0.08)',
              border: '1px solid rgba(56, 189, 248, 0.25)',
              borderRadius: '5px',
              padding: '3px 8px',
              color: '#38BDF8',
              fontSize: '11px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            <Activity size={11} />
            <span>{m.label}</span>
          </Link>
        ))}

        {/* Finding Links */}
        {findings.map((f) => (
          <Link
            key={f.id}
            to={`/diagnostics?findingId=${f.id}`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              borderRadius: '5px',
              padding: '3px 8px',
              color: '#F87171',
              fontSize: '11px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            <AlertTriangle size={11} />
            <span>Finding: {f.label}</span>
          </Link>
        ))}

        {/* Root Cause Links */}
        {rootCauses.map((rc) => (
          <Link
            key={rc.id}
            to={`/root-causes?rootCauseId=${rc.id}`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              background: 'rgba(245, 158, 11, 0.08)',
              border: '1px solid rgba(245, 158, 11, 0.25)',
              borderRadius: '5px',
              padding: '3px 8px',
              color: '#FBBF24',
              fontSize: '11px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            <GitMerge size={11} />
            <span>Root Cause: {rc.label}</span>
          </Link>
        ))}

        {/* Recommendation Links */}
        {recommendations.map((r) => (
          <Link
            key={r.id}
            to="/recommendations"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              background: 'rgba(16, 185, 129, 0.08)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: '5px',
              padding: '3px 8px',
              color: '#10B981',
              fontSize: '11px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            <Zap size={11} />
            <span>Action: {r.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};
