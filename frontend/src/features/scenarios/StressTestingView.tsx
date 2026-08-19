import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, TrendingDown, CheckCircle2, ShieldCheck, Play } from 'lucide-react';

export const StressTestingView: React.FC = () => {
  const [selectedShock, setSelectedShock] = useState<'DEMAND_COLLAPSE' | 'SUPPLY_CHAIN_SHOCK' | 'RECESSION'>('DEMAND_COLLAPSE');

  const shockData = {
    DEMAND_COLLAPSE: {
      name: 'Demand Shock (-30% Volume Contraction)',
      survival: '88.5%',
      drawdown: '-$84,000 ARR',
      recoveryTime: '45 days',
      hedges: [
        'Activate automated promotional loyalty credits to high-LTV accounts',
        'Reduce regional carrier minimum guarantee retainers by 20%',
        'Reroute 40% of standard parcel volume to consolidated economy freight',
      ],
    },
    SUPPLY_CHAIN_SHOCK: {
      name: 'Supply Chain Disruption (Secondary Hub Outage)',
      survival: '82.0%',
      drawdown: '-$112,000 ARR',
      recoveryTime: '60 days',
      hedges: [
        'Dynamically failover Southeastern volume to Northern auxiliary fulfillment nodes',
        'Enforce strict priority tiering on customer deliveries',
      ],
    },
    RECESSION: {
      name: 'Macroeconomic Recessionary Downturn',
      survival: '91.0%',
      drawdown: '-$65,000 ARR',
      recoveryTime: '30 days',
      hedges: [
        'Restructure contract renewal terms with 12-month prepay incentives',
        'Freeze non-essential marketing spend and redirect to customer win-back',
      ],
    },
  }[selectedShock];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#EF4444', fontWeight: 800 }}>
          Deterministic Tail-Risk Simulation Layer
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Strategic Stress-Testing & Macro Shock Simulator
        </h1>
      </div>

      {/* Shock Selector Tabs */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {[
          { key: 'DEMAND_COLLAPSE', label: 'Demand Collapse (-30%)' },
          { key: 'SUPPLY_CHAIN_SHOCK', label: 'Supply Chain Hub Shock' },
          { key: 'RECESSION', label: 'Economic Recession' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setSelectedShock(tab.key as any)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              background: selectedShock === tab.key ? '#EF4444' : 'rgba(15, 23, 42, 0.8)',
              color: '#FFFFFF',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Shock Impact Card */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
            {shockData.name}
          </h3>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '3px 10px', borderRadius: '12px' }}>
            Survival Probability: {shockData.survival}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '16px', borderRadius: '8px' }}>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>MAX ARR DRAWDOWN</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#EF4444', marginTop: '2px' }}>{shockData.drawdown}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>RECOVERY TIMELINE</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>{shockData.recoveryTime}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>PORTFOLIO RESILIENCE</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>HIGH</div>
          </div>
        </div>

        {/* Autonomous Hedging Prescriptions */}
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '10px' }}>
            Autonomous Hedging & Mitigation Protocols
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {shockData.hedges.map((hedge, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '12px 16px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  color: '#F1F5F9',
                }}
              >
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981' }} />
                <span>{hedge}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
