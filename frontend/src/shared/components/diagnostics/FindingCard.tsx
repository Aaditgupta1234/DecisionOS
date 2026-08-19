import React, { useState } from 'react';
import { SeverityBadge, SeverityType } from './SeverityBadge';
import {
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  TrendingDown,
  GitMerge,
  CheckCircle2,
  Activity,
  ArrowRight,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export interface FindingTraceability {
  supportingMetric?: string;
  metricDelta?: string;
  associatedRootCauseTitle?: string;
  associatedRootCauseId?: string;
  associatedRecommendationTitle?: string;
  associatedRecommendationId?: string;
  expectedRecovery?: string;
}

interface Props {
  id: string;
  title: string;
  severity: SeverityType | string;
  description: string;
  businessImpact?: string;
  affectedKpi?: string;
  confidenceScore?: number;
  createdAt?: string;
  traceability?: FindingTraceability;
}

export const FindingCard: React.FC<Props> = ({
  id,
  title,
  severity,
  description,
  businessImpact = '-$218K / quarter',
  affectedKpi = 'Revenue & Retention',
  confidenceScore = 0.91,
  createdAt = 'Aug 18, 2026',
  traceability,
}) => {
  const [expanded, setExpanded] = useState(false);
  const confidencePct = Math.round(confidenceScore > 1 ? confidenceScore : confidenceScore * 100);

  const defaultTrace: FindingTraceability = {
    supportingMetric: 'Customer Retention Rate',
    metricDelta: 'Dropped from 90.1% → 85.8% (-4.3%)',
    associatedRootCauseTitle: 'Courier Transit Delays in Southeastern Logistics Routes',
    associatedRootCauseId: 'rc_1',
    associatedRecommendationTitle: 'Targeted Win-Back Campaign & Courier SLA Penalties',
    associatedRecommendationId: 'rec_1',
    expectedRecovery: '+$180K ARR',
  };

  const trace = traceability || defaultTrace;

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '10px',
      marginBottom: '12px',
      overflow: 'hidden',
      transition: 'border-color 0.15s ease',
    }}>
      {/* Main Header Bar */}
      <div style={{ padding: '16px 20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div style={{ flex: 1, marginRight: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <SeverityBadge severity={severity} />
            <span style={{ fontSize: '11px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '11.5px', color: '#94A3B8', fontWeight: 600 }}>Affected KPI: <strong style={{ color: '#E2E8F0' }}>{affectedKpi}</strong></span>
            <span style={{ fontSize: '11px', color: '#64748B' }}>•</span>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '3px',
              fontSize: '10px',
              fontWeight: 700,
              color: '#38BDF8',
              background: 'rgba(56, 189, 248, 0.08)',
              padding: '1px 5px',
              borderRadius: '4px',
            }}>
              <ShieldCheck size={11} />
              <span>{confidencePct}% Confidence</span>
            </span>
          </div>

          <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em', marginBottom: '6px' }}>
            {title}
          </h3>

          <p style={{ fontSize: '12.5px', color: '#CBD5E1', lineHeight: 1.5, margin: 0 }}>
            {description}
          </p>
        </div>

        {/* Right Impact Pill & Drawer Toggle */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '10px' }}>
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#F87171',
            padding: '4px 10px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 800,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            whiteSpace: 'nowrap',
          }}>
            <TrendingDown size={13} />
            <span>Impact: {businessImpact}</span>
          </div>

          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            style={{
              background: 'transparent',
              border: '1px solid #1E293B',
              color: '#94A3B8',
              borderRadius: '5px',
              padding: '3px 8px',
              fontSize: '11px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
            }}
          >
            <span>{expanded ? 'Hide Traceability' : 'View Full Trace'}</span>
            {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          </button>
        </div>
      </div>

      {/* Expandable Traceability Drawer */}
      {expanded && (
        <div style={{
          background: '#05070B',
          borderTop: '1px solid #141C28',
          padding: '16px 20px',
        }}>
          <div style={{ fontSize: '10.5px', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
            Deterministic Causal Chain Traceability
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {/* 1. Supporting Metrics */}
            <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '6px', padding: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#94A3B8', fontSize: '11px', fontWeight: 600, marginBottom: '4px' }}>
                <Activity size={12} color="#38BDF8" />
                <span>1. Supporting Metric Delta</span>
              </div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', marginBottom: '2px' }}>
                {trace.supportingMetric}
              </div>
              <div style={{ fontSize: '11px', color: '#F87171', fontFamily: 'monospace' }}>
                {trace.metricDelta}
              </div>
            </div>

            {/* 2. Associated Root Cause */}
            <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '6px', padding: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#94A3B8', fontSize: '11px', fontWeight: 600, marginBottom: '4px' }}>
                <GitMerge size={12} color="#F59E0B" />
                <span>2. Root Cause Attribution</span>
              </div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
                {trace.associatedRootCauseTitle}
              </div>
              <Link to="/root-causes" style={{ fontSize: '10.5px', color: '#38BDF8', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
                <span>Inspect Causal Graph</span>
                <ArrowRight size={10} />
              </Link>
            </div>

            {/* 3. Associated Recommendation */}
            <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '6px', padding: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#94A3B8', fontSize: '11px', fontWeight: 600, marginBottom: '4px' }}>
                <CheckCircle2 size={12} color="#10B981" />
                <span>3. Recommended Next Action</span>
              </div>
              <div style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', marginBottom: '2px' }}>
                {trace.associatedRecommendationTitle}
              </div>
              <div style={{ fontSize: '11px', color: '#10B981', fontWeight: 700 }}>
                Recovery: {trace.expectedRecovery}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
