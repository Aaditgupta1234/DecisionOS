import React from 'react';
import { Activity, TrendingUp, CheckCircle2 } from 'lucide-react';

interface AttributionItem {
  initiativeTitle: string;
  liftValue: string;
  contributionPct: number;
  color: string;
}

interface Props {
  kpiName?: string;
  totalLift?: string;
  attributions?: AttributionItem[];
}

export const KPIAttributionCard: React.FC<Props> = ({
  kpiName = 'Customer Retention Rate (85.8% → 88.9%)',
  totalLift = '+3.1% Total Gain',
  attributions = [
    { initiativeTitle: 'Targeted Win-Back Campaign & Courier SLAs', liftValue: '+2.1% lift', contributionPct: 67.7, color: '#10B981' },
    { initiativeTitle: 'Secondary Hub Dispatch Load-Balancing', liftValue: '+0.7% lift', contributionPct: 22.6, color: '#38BDF8' },
    { initiativeTitle: 'Automated Post-Purchase Cross-Sell Engine', liftValue: '+0.3% lift', contributionPct: 9.7, color: '#F59E0B' },
  ],
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <div style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Deterministic KPI Attribution Engine
          </div>
          <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', margin: '2px 0 0' }}>
            {kpiName}
          </h3>
        </div>

        <div style={{
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10B981',
          padding: '4px 10px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 800,
        }}>
          {totalLift}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {attributions.map((att, idx) => (
          <div
            key={idx}
            style={{
              background: '#05070B',
              border: '1px solid #141C28',
              borderRadius: '8px',
              padding: '10px 14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ flex: 1, marginRight: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF' }}>{att.initiativeTitle}</span>
                <span style={{ fontSize: '12px', fontWeight: 800, color: att.color }}>{att.liftValue}</span>
              </div>

              {/* Progress Bar */}
              <div style={{ width: '100%', height: '4px', background: '#111827', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{ width: `${att.contributionPct}%`, height: '100%', background: att.color }} />
              </div>
            </div>

            <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 700, width: '45px', textAlign: 'right' }}>
              {att.contributionPct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
