import React, { useState } from 'react';
import { DollarSign, TrendingUp, Sparkles, PieChart, ShieldCheck, CheckCircle2, ArrowRight, Activity } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export interface CapitalAllocationOutcome {
  id: string;
  quarter: string;
  unit: string;
  recommendedPct: string;
  actualAllocatedPct: string;
  expectedArr: string;
  actualRealizedArr: string;
  accuracyScore: number;
}

export const CapitalAllocationStudioView: React.FC = () => {
  const [budget] = useState(1000000);
  const [strategyExecuted, setStrategyExecuted] = useState(false);
  const [activeTab, setActiveTab] = useState<'OPTIMIZATION' | 'REALIZED_OUTCOMES'>('OPTIMIZATION');

  const historicalOutcomes: CapitalAllocationOutcome[] = [
    {
      id: 'out-1',
      quarter: 'Q4 2025 Allocation Cycle',
      unit: 'Enterprise B2B SaaS Division',
      recommendedPct: '62%',
      actualAllocatedPct: '58%',
      expectedArr: '+$480,000 ARR',
      actualRealizedArr: '+$451,000 ARR',
      accuracyScore: 93.9,
    },
    {
      id: 'out-2',
      quarter: 'Q4 2025 Allocation Cycle',
      unit: 'North America Retail Logistics',
      recommendedPct: '28%',
      actualAllocatedPct: '30%',
      expectedArr: '+$140,000 ARR',
      actualRealizedArr: '+$138,000 ARR',
      accuracyScore: 98.5,
    },
    {
      id: 'out-3',
      quarter: 'Q3 2025 Allocation Cycle',
      unit: 'Cloud Analytics Infrastructure',
      recommendedPct: '50%',
      actualAllocatedPct: '50%',
      expectedArr: '+$310,000 ARR',
      actualRealizedArr: '+$312,000 ARR',
      accuracyScore: 99.3,
    },
  ];

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

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', padding: '3px' }}>
            <button
              onClick={() => setActiveTab('OPTIMIZATION')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'OPTIMIZATION' ? '#38BDF8' : 'transparent',
                color: activeTab === 'OPTIMIZATION' ? '#090D14' : '#94A3B8',
                fontWeight: 700,
                fontSize: '0.76rem',
                cursor: 'pointer',
              }}
            >
              $1M Optimization Model
            </button>
            <button
              onClick={() => setActiveTab('REALIZED_OUTCOMES')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'REALIZED_OUTCOMES' ? '#10B981' : 'transparent',
                color: activeTab === 'REALIZED_OUTCOMES' ? '#090D14' : '#94A3B8',
                fontWeight: 700,
                fontSize: '0.76rem',
                cursor: 'pointer',
              }}
            >
              Outcome Attribution Tracking
            </button>
          </div>

          <Button
            variant="primary"
            size="sm"
            icon={<Sparkles size={14} />}
            onClick={() => setStrategyExecuted(true)}
          >
            Execute $1M Strategy
          </Button>
        </div>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL CAPITAL BUDGET" value="$1,000,000" sublabel="Q1/Q2 Discretionary Growth Fund" valueColor="#FFFFFF" />
        <MetricTile label="EXPECTED NET VALUE (ARR)" value="+$601,800" sublabel="Blended ROI: 6.02x Multiple" valueColor="#10B981" />
        <MetricTile label="HISTORICAL ACCURACY" value="97.2%" sublabel="Realized ARR vs Modeled ROI" valueColor="#38BDF8" />
        <MetricTile label="GOVERNANCE CLEARANCE" value="APPROVED" sublabel="Within CFO & Board Discretionary Limits" valueColor="#A855F7" />
      </div>

      {activeTab === 'REALIZED_OUTCOMES' ? (
        /* Realized Capital Allocation Outcomes Ledger */
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>
              Historical Capital Allocation Outcome Attribution
            </span>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Closed-Loop Capital ROI</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {historicalOutcomes.map((o) => (
              <div
                key={o.id}
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
                    <span style={{ fontSize: '0.96rem', fontWeight: 800, color: '#FFFFFF' }}>{o.unit}</span>
                    <Badge variant="emerald" size="sm">
                      {o.accuracyScore}% Accuracy
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                    Cycle: {o.quarter} • Recommended: <strong>{o.recommendedPct}</strong> • Actual: <strong>{o.actualAllocatedPct}</strong> • Expected: {o.expectedArr}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 900, color: '#10B981', padding: '6px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px' }}>
                    Realized: {o.actualRealizedArr}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : (
        /* Capital Allocation Recommendations Table */
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
      )}
    </div>
  );
};
