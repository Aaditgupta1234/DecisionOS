import React, { useState } from 'react';
import { Layers, DollarSign, ShieldCheck, TrendingUp, CheckCircle2, Play, Sparkles } from 'lucide-react';

export const PortfolioOptimizerView: React.FC = () => {
  const [budgetCap, setBudgetCap] = useState(500000);
  const [riskTolerance, setRiskTolerance] = useState(20.0);

  const optimizationResults = {
    allocatedBudget: '$90,800',
    expectedArr: '+$258,000',
    aggregateRisk: '15.3 (Within Cap)',
    aggregateRoi: '2.84x ROI',
    allocations: [
      { name: 'Retention First + Courier SLA Rebalance', budget: '$25,800', arr: '+$124,000', risk: '14.1', status: 'OPTIMAL_ALLOCATION' },
      { name: 'Northern Hub Regional Expansion', budget: '$65,000', arr: '+$134,000', risk: '16.5', status: 'APPROVED_SUBSET' },
      { name: 'Broad Paid Acquisition Campaign', budget: '$120,000', arr: '+$98,000', risk: '24.8', status: 'EXCEEDS_RISK_CAP' },
    ],
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
          Multi-Scenario Constrained Capital Allocation
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Portfolio-Wide Scenario Optimizer
        </h1>
      </div>

      {/* Inputs & Constraints */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>Max Portfolio Budget Cap</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#38BDF8' }}>${budgetCap.toLocaleString()}</span>
          </div>
          <input
            type="range"
            min="100000"
            max="1000000"
            step="50000"
            value={budgetCap}
            onChange={(e) => setBudgetCap(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#38BDF8', cursor: 'pointer' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>Max Systemic Risk Tolerance</span>
            <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#F59E0B' }}>{riskTolerance}</span>
          </div>
          <input
            type="range"
            min="10"
            max="40"
            step="1"
            value={riskTolerance}
            onChange={(e) => setRiskTolerance(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: '#F59E0B', cursor: 'pointer' }}
          />
        </div>
      </div>

      {/* Optimization Solution */}
      <div style={{ background: '#090D14', border: '1px solid #10B981', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.72rem', color: '#10B981', fontWeight: 800, textTransform: 'uppercase' }}>
            Optimal Knapsack Allocation Solution
          </span>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981' }}>
            ★ Highest Risk-Adjusted Return
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '16px', borderRadius: '8px' }}>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>TOTAL ALLOCATED BUDGET</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>{optimizationResults.allocatedBudget}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>AGGREGATE ARR YIELD</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>{optimizationResults.expectedArr}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>AGGREGATE RISK</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>{optimizationResults.aggregateRisk}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>CAPITAL MULTIPLIER</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#A855F7', marginTop: '2px' }}>{optimizationResults.aggregateRoi}</div>
          </div>
        </div>

        {/* Selected Scenarios Table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {optimizationResults.allocations.map((a, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                background: a.status === 'OPTIMAL_ALLOCATION' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(15, 23, 42, 0.6)',
                border: `1px solid ${a.status === 'OPTIMAL_ALLOCATION' ? '#10B981' : '#1E293B'}`,
                borderRadius: '8px',
              }}
            >
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#FFFFFF' }}>{a.name}</div>
              <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
                <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>Cost: {a.budget}</span>
                <span style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700 }}>ARR: {a.arr}</span>
                <span style={{ fontSize: '0.68rem', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', background: a.status === 'OPTIMAL_ALLOCATION' ? '#10B981' : 'rgba(30, 41, 59, 0.8)', color: a.status === 'OPTIMAL_ALLOCATION' ? '#090D14' : '#94A3B8' }}>
                  {a.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
