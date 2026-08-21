import React from 'react';
import { X, GitMerge, AlertTriangle, CheckCircle2, Zap, ArrowRight, ShieldCheck, Clock, Target, ListOrdered } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  recommendation?: {
    id: string;
    title: string;
    actionSummary: string;
    whyRecommended?: string;
    priority?: string;
    difficulty?: string;
    confidence?: number;
    expectedRecovery?: string;
    status?: string;
    rootCauseId?: string;
    rootCauseTitle?: string;
    findingId?: string;
    findingTitle?: string;
    expectedMetric?: string;
    baseline?: number | string;
    target?: number | string;
    measurementPeriod?: string;
    actionPlan?: string[];
    evidence?: Record<string, any>;
  };
}

export const RecommendationDrawer: React.FC<Props> = ({
  isOpen,
  onClose,
  recommendation,
}) => {
  if (!isOpen || !recommendation) return null;

  const rootCauseId = recommendation.rootCauseId || 'rc_1';
  const findingId = recommendation.findingId || 'f_1';
  const actionSteps = recommendation.actionPlan || [];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '580px',
      background: '#070A0F',
      borderLeft: '1px solid #1E293B',
      boxShadow: '-20px 0 50px rgba(0, 0, 0, 0.85)',
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      color: '#FFFFFF',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      {/* Drawer Header */}
      <div style={{ padding: '20px 24px', borderBottom: '1px solid #141C28', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Zap size={16} color="#10B981" />
          <span style={{ fontSize: '12px', fontWeight: 800, color: '#10B981', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Executive Action Blueprint
          </span>
        </div>

        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: '#94A3B8', cursor: 'pointer', padding: '4px' }}
        >
          <X size={18} />
        </button>
      </div>

      {/* Drawer Body */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
        
        {/* Title & Priority Strip */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#F59E0B', background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.28)', padding: '2px 7px', borderRadius: '4px' }}>
            {recommendation.priority || 'HIGH'} PRIORITY
          </span>
          <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#94A3B8', background: '#111622', padding: '2px 7px', borderRadius: '4px' }}>
            {recommendation.difficulty || 'LOW'} DIFFICULTY
          </span>
          <span style={{ fontSize: '10px', fontWeight: 700, color: '#64748B', background: 'rgba(255, 255, 255, 0.05)', padding: '2px 7px', borderRadius: '4px' }}>
            STATUS: {recommendation.status || 'PENDING'}
          </span>
        </div>

        <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '8px' }}>
          {recommendation.title}
        </h2>

        <p style={{ fontSize: '13px', color: '#CBD5E1', lineHeight: 1.6, marginBottom: '16px' }}>
          {recommendation.actionSummary}
        </p>

        {/* Why Recommended Explainability Narrative */}
        {recommendation.whyRecommended && (
          <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '8px', padding: '12px 14px', marginBottom: '20px' }}>
            <span style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 700, textTransform: 'uppercase', display: 'block', marginBottom: '4px' }}>
              Why Recommended (Causal & Rule Evidence)
            </span>
            <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0, lineHeight: 1.5 }}>
              {recommendation.whyRecommended}
            </p>
          </div>
        )}

        {/* Target Metric Outcomes Card */}
        <div style={{
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Target size={15} color="#10B981" />
              <span style={{ fontSize: '11px', color: '#10B981', textTransform: 'uppercase', fontWeight: 800 }}>
                Target Metric Outcome & Baseline
              </span>
            </div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldCheck size={14} />
              <span>{recommendation.confidence || 90}% Confidence</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr', gap: '12px', background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '12px' }}>
            <div>
              <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', display: 'block', fontWeight: 600 }}>Target Metric</span>
              <span style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>{recommendation.expectedMetric || 'Total Revenue'}</span>
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', display: 'block', fontWeight: 600 }}>Baseline</span>
              <span style={{ fontSize: '13px', fontWeight: 800, color: '#F87171' }}>{recommendation.baseline ?? '-16.7'}</span>
            </div>
            <div>
              <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', display: 'block', fontWeight: 600 }}>Target Goal</span>
              <span style={{ fontSize: '13px', fontWeight: 800, color: '#10B981' }}>{recommendation.target ?? '-15.03'}</span>
            </div>
          </div>

          <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={12} color="#64748B" />
            <span>Measurement Window: <strong>{recommendation.measurementPeriod || '90 days'}</strong></span>
          </div>
        </div>

        {/* Ordered Action Steps */}
        {actionSteps.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', fontWeight: 700, color: '#E2E8F0', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '12px' }}>
              <ListOrdered size={14} color="#38BDF8" />
              <span>Prescribed Execution Action Steps ({actionSteps.length})</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {actionSteps.map((step, idx) => (
                <div key={idx} style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px', display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                  <span style={{ fontSize: '11px', fontWeight: 900, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', padding: '1px 6px', borderRadius: '4px' }}>
                    0{idx + 1}
                  </span>
                  <p style={{ fontSize: '12px', color: '#CBD5E1', margin: 0, lineHeight: 1.4 }}>
                    {step}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 2-Way Causal Navigation Links */}
        <div style={{
          background: '#0B0F17',
          border: '1px solid #1A2230',
          borderRadius: '8px',
          padding: '14px 16px',
          marginBottom: '24px',
        }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '10px' }}>
            Deep Causal Navigation Trail
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Link
              to={`/diagnostics`}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: '#05070B',
                border: '1px solid #141C28',
                padding: '10px 12px',
                borderRadius: '6px',
                color: '#FFFFFF',
                textDecoration: 'none',
                fontSize: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={14} color="#EF4444" />
                <span style={{ fontWeight: 600 }}>Inspect Triggering Diagnostic Findings</span>
              </div>
              <ArrowRight size={13} color="#38BDF8" />
            </Link>
          </div>
        </div>

      </div>

      {/* Drawer Footer */}
      <div style={{ padding: '16px 24px', borderTop: '1px solid #141C28', display: 'flex', justifyContent: 'flex-end' }}>
        <button
          onClick={onClose}
          style={{
            background: '#111622',
            border: '1px solid #1F2738',
            color: '#FFFFFF',
            padding: '8px 18px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Close Blueprint
        </button>
      </div>
    </div>
  );
};
