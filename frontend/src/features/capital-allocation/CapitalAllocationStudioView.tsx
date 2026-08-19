import React, { useState } from 'react';
import { DollarSign, TrendingUp, Sparkles, PieChart, ShieldCheck, CheckCircle2, ArrowRight } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const CapitalAllocationStudioView: React.FC = () => {
  const [budget] = useState(1000000);
  const [strategyExecuted, setStrategyExecuted] = useState(false);

  const allocations = [
    {
      unit: 'Enterprise B2B SaaS Division',
      currentArr: '$4.2M',
      roiMultiple: '7.2x',
      recommendedPct: '62%',
      recommendedDollar: '$620,000',
      expectedArrGain: '+$446,400 ARR',
      riskTier: 'LOW',
    },
    {
      unit: 'North America Retail Logistics',
      currentArr: '$5.8M',
      roiMultiple: '4.8x',
      recommendedPct: '28%',
      recommendedDollar: '$280,000',
      expectedArrGain: '+$134,400 ARR',
      riskTier: 'LOW',
    },
    {
      unit: 'APAC Cross-Border Freight',
      currentArr: '$2.4M',
      roiMultiple: '2.1x',
      recommendedPct: '10%',
      recommendedDollar: '$100,000',
      expectedArrGain: '+$21,000 ARR',
      riskTier: 'MODERATE',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
            Enterprise Capital Deployment & ROI Optimization
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Capital Allocation Intelligence Studio ($1M Investment)
          </h1>
        </div>

        <Button
          variant="primary"
          size="sm"
          icon={<Sparkles size={14} />}
          onClick={() => setStrategyExecuted(true)}
        >
          Execute $1M Capital Reallocation Strategy
        </Button>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL CAPITAL BUDGET" value="$1,000,000" sublabel="Q1/Q2 Discretionary Growth Fund" valueColor="#FFFFFF" />
        <MetricTile label="EXPECTED NET VALUE (ARR)" value="+$601,800" sublabel="Blended ROI: 6.02x Multiple" valueColor="#10B981" />
        <MetricTile label="PRIMARY ALLOCATION" value="62% to SaaS" sublabel="Highest Efficiency Curve (7.2x)" valueColor="#A855F7" />
        <MetricTile label="GOVERNANCE CLEARANCE" value="APPROVED" sublabel="Within CFO & Board Discretionary Limits" valueColor="#38BDF8" />
      </div>

      {/* Capital Allocation Recommendations Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Mathematical Capital Allocation Ledger</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Portfolio Elasticity Optimization</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {allocations.map((a, idx) => (
            <div
              key={idx}
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
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{a.unit}</span>
                  <Badge variant={a.roiMultiple.startsWith('7') ? 'purple' : 'emerald'} size="sm">
                    ROI: {a.roiMultiple}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Allocation: <strong style={{ color: '#38BDF8' }}>{a.recommendedPct} ({a.recommendedDollar})</strong> • Expected ARR: <strong style={{ color: '#10B981' }}>{a.expectedArrGain}</strong>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#FFFFFF', padding: '4px 12px', borderRadius: '6px', background: 'rgba(168, 85, 247, 0.15)', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
                  {a.recommendedDollar}
                </span>
              </div>
            </div>
          ))}
        </div>

        {strategyExecuted && (
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <CheckCircle2 size={18} color="#10B981" />
              <span style={{ fontSize: '0.84rem', color: '#F1F5F9' }}>
                Capital Allocation Strategy dispatched to Governance Decision Registry: <strong>DEC-2026-045 (+$601,800 Net Expected ARR)</strong>
              </span>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};
