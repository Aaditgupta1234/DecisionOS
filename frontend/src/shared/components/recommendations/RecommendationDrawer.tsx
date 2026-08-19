import React from 'react';
import { X, GitMerge, AlertTriangle, CheckCircle2, Zap, ArrowRight, ShieldCheck, Clock, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  recommendation?: {
    id: string;
    title: string;
    actionSummary: string;
    priority?: string;
    difficulty?: string;
    confidence?: number;
    expectedRecovery?: string;
    status?: string;
    rootCauseId?: string;
    rootCauseTitle?: string;
    findingId?: string;
    findingTitle?: string;
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

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '560px',
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
            Executive Implementation Blueprint
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
            STATUS: {recommendation.status || 'NOT_STARTED'}
          </span>
        </div>

        <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '8px' }}>
          {recommendation.title}
        </h2>

        <p style={{ fontSize: '13px', color: '#CBD5E1', lineHeight: 1.6, marginBottom: '20px' }}>
          {recommendation.actionSummary}
        </p>

        {/* Expected Financial ROI Box */}
        <div style={{
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>
              Projected Annualized Recovery
            </span>
            <div style={{ fontSize: '22px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>
              {recommendation.expectedRecovery || '+$180K ARR'}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Confidence</span>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#38BDF8', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <ShieldCheck size={14} />
              <span>{recommendation.confidence || 92}% Confidence</span>
            </div>
          </div>
        </div>

        {/* 2-Way Causal Deep-Link Navigation Links */}
        <div style={{
          background: '#0B0F17',
          border: '1px solid #1A2230',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
        }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '10px' }}>
            Deep Causal Navigation Trail
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {/* Link 1: View Root Cause */}
            <Link
              to={`/root-causes?rootCauseId=${rootCauseId}`}
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
                <GitMerge size={14} color="#F59E0B" />
                <span style={{ fontWeight: 600 }}>View Associated Root Cause</span>
              </div>
              <ArrowRight size={13} color="#38BDF8" />
            </Link>

            {/* Link 2: View Diagnostic Finding */}
            <Link
              to={`/diagnostics?findingId=${findingId}`}
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
                <span style={{ fontWeight: 600 }}>View Triggering Diagnostic Finding</span>
              </div>
              <ArrowRight size={13} color="#38BDF8" />
            </Link>
          </div>
        </div>

        {/* Phased Implementation Guidance */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#E2E8F0', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '12px' }}>
            Phased 4-Week Execution Roadmap
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#38BDF8' }}>Week 1: SLA Enforcement</span>
                <span style={{ fontSize: '10px', color: '#64748B' }}>Operations</span>
              </div>
              <p style={{ fontSize: '11.5px', color: '#94A3B8', margin: 0 }}>Notify regional couriers in SE hubs of strict 3-day SLA compliance thresholds with automated contract penalties.</p>
            </div>

            <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#38BDF8' }}>Week 2: Audience Segmentation</span>
                <span style={{ fontSize: '10px', color: '#64748B' }}>Marketing</span>
              </div>
              <p style={{ fontSize: '11.5px', color: '#94A3B8', margin: 0 }}>Filter the 842 churn-risk customers impacted by courier transit delays into an automated recovery cohort.</p>
            </div>

            <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#38BDF8' }}>Week 3–4: Incentive Launch & Measurement</span>
                <span style={{ fontSize: '10px', color: '#64748B' }}>Growth</span>
              </div>
              <p style={{ fontSize: '11.5px', color: '#94A3B8', margin: 0 }}>Deploy personalized win-back credit incentives with deterministic repeat purchase telemetry tracking.</p>
            </div>
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
