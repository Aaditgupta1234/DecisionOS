import React from 'react';
import { AlertTriangle, ShieldCheck, ShieldAlert, CheckCircle2 } from 'lucide-react';

export interface InitiativeRiskItem {
  id: string;
  title: string;
  impactLevel: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  owner: string;
  mitigationPlan: string;
  status: 'MITIGATED' | 'MONITORING' | 'ACTION_REQUIRED';
}

interface Props {
  risks?: InitiativeRiskItem[];
}

export const InitiativeRiskPanel: React.FC<Props> = ({
  risks = [
    {
      id: 'r-1',
      title: 'Courier Carrier API Integration Latency',
      impactLevel: 'HIGH',
      owner: 'Logistics Tech Lead',
      mitigationPlan: 'Established manual daily SLA CSV reconciliation export until automated webhook deployment completes.',
      status: 'MONITORING',
    },
    {
      id: 'r-2',
      title: 'Audience Credit Incentive Email Bounce Rates',
      impactLevel: 'MEDIUM',
      owner: 'Growth Marketing Lead',
      mitigationPlan: 'Enforced zero-bounce email verification gateway prior to batch dispatch of the 842 churn-risk customer vouchers.',
      status: 'MITIGATED',
    },
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={16} color="#EF4444" />
          <h3 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Initiative Risk Register & Execution Blocker Mitigations
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>
          {risks.length} Active Vectors Tracked
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {risks.map((r) => (
          <div
            key={r.id}
            style={{
              background: '#05070B',
              border: '1px solid #141C28',
              borderRadius: '8px',
              padding: '12px 14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{
                  fontSize: '9.5px',
                  fontWeight: 800,
                  color: r.impactLevel === 'HIGH' ? '#F59E0B' : '#38BDF8',
                  background: 'rgba(255, 255, 255, 0.04)',
                  padding: '1px 6px',
                  borderRadius: '4px',
                }}>
                  {r.impactLevel} RISK
                </span>
                <span style={{ fontSize: '12.5px', fontWeight: 700, color: '#FFFFFF' }}>{r.title}</span>
              </div>

              <span style={{
                fontSize: '10px',
                fontWeight: 700,
                color: r.status === 'MITIGATED' ? '#10B981' : '#F59E0B',
                display: 'flex',
                alignItems: 'center',
                gap: '3px',
              }}>
                {r.status === 'MITIGATED' ? <CheckCircle2 size={11} /> : <AlertTriangle size={11} />}
                <span>{r.status}</span>
              </span>
            </div>

            <div style={{ fontSize: '11.5px', color: '#CBD5E1', lineHeight: 1.4, marginBottom: '6px' }}>
              <strong style={{ color: '#94A3B8' }}>Mitigation Action:</strong> {r.mitigationPlan}
            </div>

            <span style={{ fontSize: '10.5px', color: '#64748B' }}>Owner: {r.owner}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
