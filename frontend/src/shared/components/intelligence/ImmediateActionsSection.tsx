import React from 'react';
import { AlertCircle, CheckCircle2, ArrowRight, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ActionItem {
  id: string;
  rank: number;
  title: string;
  expectedOutcome: string;
  owner: string;
  timeframe: string;
}

interface Props {
  actions?: ActionItem[];
}

export const ImmediateActionsSection: React.FC<Props> = ({
  actions = [
    {
      id: 'a1',
      rank: 1,
      title: 'Launch Targeted Win-Back Campaign for Southeastern Corridors',
      expectedOutcome: 'Recovers +$180K ARR by mitigating 48% of active customer churn velocity',
      owner: 'Growth & Marketing',
      timeframe: 'Immediate (Next 7 Days)',
    },
    {
      id: 'a2',
      title: 'Enforce Courier SLA Transit Caps & Re-Route Secondary Hubs',
      rank: 2,
      expectedOutcome: 'Lowers transit times back under 3.0 days, resolving 2 critical delivery bottlenecks',
      owner: 'Logistics Operations',
      timeframe: 'Weeks 1–2',
    },
    {
      id: 'a3',
      title: 'Deploy Automated Cross-Sell Recommendations on High-Value Checkouts',
      rank: 3,
      expectedOutcome: 'Lifts average order value by +$16.70 across Health & Beauty category transactions',
      owner: 'Product & Merchandising',
      timeframe: 'Weeks 2–3',
    },
  ],
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #0D131F 0%, #080C14 100%)',
      border: '1px solid rgba(56, 189, 248, 0.3)',
      borderRadius: '12px',
      padding: '22px 24px',
      marginBottom: '24px',
      boxShadow: '0 15px 35px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(56, 189, 248, 0.15)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Zap size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em', margin: 0, textTransform: 'uppercase' }}>
            Section 5: Immediate Leadership Actions Required
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 700, background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
          CEO Executive Summary
        </span>
      </div>

      <p style={{ fontSize: '12.5px', color: '#94A3B8', lineHeight: 1.5, marginBottom: '16px' }}>
        Based on deterministic causal attribution of the active dataset, leadership should authorize the following three priority actions immediately:
      </p>

      {/* Action Items List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {actions.map((act) => (
          <div
            key={act.id}
            style={{
              background: '#04070C',
              border: '1px solid #141D2B',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <span style={{
                width: '22px',
                height: '22px',
                borderRadius: '50%',
                background: '#1D4ED8',
                color: '#FFFFFF',
                fontSize: '11px',
                fontWeight: 800,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                marginTop: '2px',
              }}>
                {act.rank}
              </span>

              <div>
                <div style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF', marginBottom: '2px' }}>
                  {act.title}
                </div>
                <div style={{ fontSize: '12px', color: '#CBD5E1', lineHeight: 1.4 }}>
                  {act.expectedOutcome}
                </div>
              </div>
            </div>

            <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: '16px' }}>
              <span style={{ fontSize: '10px', color: '#64748B', display: 'block', textTransform: 'uppercase' }}>{act.owner}</span>
              <span style={{ fontSize: '11.5px', color: '#38BDF8', fontWeight: 700 }}>{act.timeframe}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
