import React, { useState } from 'react';
import {
  Activity,
  Cpu,
  TrendingUp,
  ShieldAlert,
  Clock,
  Zap,
  Sliders,
  Sparkles,
  GitBranch,
  Layers,
  ArrowUpRight,
  Database,
  History,
  CheckCircle2,
} from 'lucide-react';
import { AIScenarioAnalystModal } from './AIScenarioAnalystModal';

export const DigitalTwinWorkspaceView: React.FC = () => {
  const [selectedSnapshot, setSelectedSnapshot] = useState<'CURRENT' | 'JANUARY' | 'APRIL'>('CURRENT');
  const [isAIAnalystOpen, setIsAIAnalystOpen] = useState(false);

  const twinDimensions = {
    CURRENT: {
      revenue: '$2,400,000',
      arr: '$2,800,000',
      retention: '84.2%',
      latency: '3.4 days',
      risk: '14.1 (Low)',
      capacity: '78.5%',
      forecast: '88.4%',
      status: 'OPTIMAL_OPERATING_ENVELOPE',
      health: 85.0,
      arrDelta: '+$124K Realized Recovery',
    },
    JANUARY: {
      revenue: '$2,280,000',
      arr: '$2,676,000',
      retention: '79.5%',
      latency: '5.4 days',
      risk: '24.3 (Elevated)',
      capacity: '88.0%',
      forecast: '82.1%',
      status: 'BOTTLENECK_IDENTIFIED',
      health: 74.0,
      arrDelta: 'Baseline State',
    },
    APRIL: {
      revenue: '$2,400,000',
      arr: '$2,800,000',
      retention: '84.2%',
      latency: '3.4 days',
      risk: '14.1 (Low)',
      capacity: '78.5%',
      forecast: '88.4%',
      status: 'OPTIMAL_OPERATING_ENVELOPE',
      health: 85.0,
      arrDelta: '+$124K Verified Realization',
    },
  }[selectedSnapshot];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            Living Mathematical Business Simulation Layer
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Digital Twin Workspace
          </h1>
        </div>

        {/* Snapshot Cadence Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', padding: '4px', borderRadius: '8px' }}>
            <History size={14} color="#94A3B8" style={{ marginLeft: '6px' }} />
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginRight: '4px' }}>Timeline:</span>
            {(['CURRENT', 'JANUARY', 'APRIL'] as const).map((snap) => (
              <button
                key={snap}
                onClick={() => setSelectedSnapshot(snap)}
                style={{
                  padding: '5px 12px',
                  borderRadius: '6px',
                  border: 'none',
                  background: selectedSnapshot === snap ? '#0284C7' : 'transparent',
                  color: selectedSnapshot === snap ? '#FFFFFF' : '#94A3B8',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                {snap === 'CURRENT' ? 'Live Twin' : snap}
              </button>
            ))}
          </div>

          <button
            onClick={() => setIsAIAnalystOpen(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              background: 'linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)',
              border: 'none',
              borderRadius: '8px',
              color: '#FFFFFF',
              fontSize: '0.8rem',
              fontWeight: 800,
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(124, 58, 237, 0.3)',
            }}
          >
            <Sparkles size={14} />
            <span>Ask AI Scenario Analyst</span>
          </button>
        </div>
      </div>

      {/* Hero Overview State */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(9, 13, 20, 0.95) 100%)',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          padding: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '18px',
        }}
      >
        <div style={{ borderRight: '1px solid #1E293B', paddingRight: '16px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>PORTFOLIO HEALTH</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#10B981', marginTop: '4px' }}>
            {twinDimensions.health} <span style={{ fontSize: '0.85rem', color: '#38BDF8' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700, marginTop: '2px' }}>
            {twinDimensions.arrDelta}
          </div>
        </div>

        <div style={{ borderRight: '1px solid #1E293B', paddingRight: '16px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>ANNUAL RUN-RATE (ARR)</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#FFFFFF', marginTop: '4px' }}>
            {twinDimensions.arr}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Revenue: {twinDimensions.revenue}</div>
        </div>

        <div style={{ borderRight: '1px solid #1E293B', paddingRight: '16px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>RETENTION & LATENCY</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#38BDF8', marginTop: '4px' }}>
            {twinDimensions.retention}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Delivery: {twinDimensions.latency}</div>
        </div>

        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>SYSTEMIC RISK & CAPACITY</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#F59E0B', marginTop: '4px' }}>
            {twinDimensions.risk}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Capacity Util: {twinDimensions.capacity}</div>
        </div>
      </div>

      {/* 7-Dimensional Living Digital Twin Matrix */}
      <div>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '14px' }}>
          Living Digital Twin Mathematical Dimensions
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {[
            { label: 'Customer Retention Velocity', val: twinDimensions.retention, sub: 'Target: >85.0%', color: '#10B981', status: 'STABILIZED' },
            { label: 'Delivery Latency Vector', val: twinDimensions.latency, sub: 'Target: <3.5 days', color: '#38BDF8', status: 'OPTIMAL' },
            { label: 'Capacity Utilization', val: twinDimensions.capacity, sub: 'Limit: 90.0%', color: '#A855F7', status: 'IN_BOUNDS' },
            { label: 'Forecast Reliability', val: twinDimensions.forecast, sub: 'Rolling 3-Cycle Accuracy', color: '#10B981', status: 'HIGH_CERTAINTY' },
            { label: 'Courier SLA Penalty Rate', val: '15.0%', sub: 'Enforced on bottom 20%', color: '#F59E0B', status: 'ACTIVE' },
            { label: 'Systemic Resilience Index', val: '88.5%', sub: 'Drawdown Tolerance: $120K', color: '#38BDF8', status: 'RESILIENT' },
          ].map((card, idx) => (
            <div
              key={idx}
              style={{
                background: '#090D14',
                border: '1px solid #1E293B',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>
                  {card.label}
                </span>
                <span style={{ fontSize: '0.68rem', fontWeight: 800, color: card.color, background: 'rgba(15, 23, 42, 0.8)', padding: '2px 6px', borderRadius: '4px' }}>
                  {card.status}
                </span>
              </div>
              <div style={{ fontSize: '1.6rem', fontWeight: 900, color: '#FFFFFF' }}>{card.val}</div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{card.sub}</div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Scenario Analyst Modal */}
      <AIScenarioAnalystModal
        isOpen={isAIAnalystOpen}
        onClose={() => setIsAIAnalystOpen(false)}
      />
    </div>
  );
};
