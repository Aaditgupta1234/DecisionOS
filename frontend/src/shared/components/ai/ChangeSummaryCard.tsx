import React from 'react';
import { TrendingUp, TrendingDown, GitCompare, ShieldCheck, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';

export const ChangeSummaryCard: React.FC = () => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #0A121E 0%, #060A10 100%)',
      border: '1px solid #1E293B',
      borderRadius: '12px',
      padding: '20px 22px',
      marginBottom: '24px',
      boxShadow: '0 12px 30px rgba(0, 0, 0, 0.6)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em', margin: 0, textTransform: 'uppercase' }}>
            What Changed Since Last Analysis Run?
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>
          Compared to RUN-2026-0810-02 (7 days ago)
        </span>
      </div>

      {/* Delta Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {/* Health Score Delta */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Health Score Delta</span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '3px' }}>
            <span style={{ fontSize: '17px', fontWeight: 800, color: '#FFFFFF' }}>82 → 85</span>
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#10B981', display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
              <TrendingUp size={12} /> +3 pts
            </span>
          </div>
        </div>

        {/* Critical Risks Delta */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Critical Risks Mitigated</span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '3px' }}>
            <span style={{ fontSize: '17px', fontWeight: 800, color: '#FFFFFF' }}>5 → 2</span>
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#10B981', display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
              <CheckCircle2 size={12} /> -3 Critical
            </span>
          </div>
        </div>

        {/* Recovery Opportunity Delta */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Identified Upside Opportunity</span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '3px' }}>
            <span style={{ fontSize: '17px', fontWeight: 800, color: '#FFFFFF' }}>$320K → $480K</span>
            <span style={{ fontSize: '11px', fontWeight: 800, color: '#38BDF8', display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
              <TrendingUp size={12} /> +$160K ARR
            </span>
          </div>
        </div>
      </div>

      {/* Largest Improvement vs Deterioration Highlights */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.22)', borderRadius: '8px', padding: '10px 14px' }}>
          <div style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            ✓ Largest Operational Improvement
          </div>
          <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#FFFFFF' }}>
            Fulfillment SLA Compliance (+14%)
          </div>
          <p style={{ fontSize: '11px', color: '#94A3B8', margin: '2px 0 0' }}>
            Secondary hub dispatch balancing reduced warehouse backlog by 2.4 days.
          </p>
        </div>

        <div style={{ background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.22)', borderRadius: '8px', padding: '10px 14px' }}>
          <div style={{ fontSize: '10.5px', color: '#F87171', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            ⚠ Largest Metric Deterioration
          </div>
          <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#FFFFFF' }}>
            Customer Retention in SE Logistics (-4.3%)
          </div>
          <p style={{ fontSize: '11px', color: '#94A3B8', margin: '2px 0 0' }}>
            Courier delays triggered acute review score drops (4.7★ → 2.1★) and elevated cart cancellations.
          </p>
        </div>
      </div>
    </div>
  );
};
