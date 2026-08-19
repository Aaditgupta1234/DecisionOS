import React from 'react';
import { ShieldAlert, AlertTriangle, Users, Globe, ArrowRight } from 'lucide-react';
import { Card, Badge, MetricTile, Button } from '../../design-system';

export const RiskConcentrationRadarView: React.FC = () => {
  const customerRisks = [
    {
      customerName: 'Enterprise Client #104 (MegaCorp Global)',
      arrShare: '$3.4M (27.4% ARR)',
      contractRenewal: 'Q3 2026',
      healthScore: '82.0 (MODERATE)',
      riskLevel: 'HIGH_CONCENTRATION',
    },
    {
      customerName: 'Enterprise Client #209 (Apex Logistics Group)',
      arrShare: '$2.8M (22.5% ARR)',
      contractRenewal: 'Q4 2026',
      healthScore: '89.4 (HEALTHY)',
      riskLevel: 'HIGH_CONCENTRATION',
    },
    {
      customerName: 'Enterprise Client #312 (Titan Retail Corp)',
      arrShare: '$2.7M (21.7% ARR)',
      contractRenewal: 'Q2 2026',
      healthScore: '74.2 (AT_RISK)',
      riskLevel: 'CRITICAL_CONCENTRATION',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#EF4444', fontWeight: 800 }}>
          Boardroom Risk Governance & Exposure Radar
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Enterprise Revenue & Customer Concentration Radar
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOP 3 CUSTOMER EXPOSURE" value="71.6% ARR" sublabel="$8.9M of $12.4M Dependent on 3 Accounts" valueColor="#EF4444" />
        <MetricTile label="REGIONAL GEOGRAPHIC RISK" value="59.7% NA" sublabel="North America Heavy Concentration" valueColor="#F59E0B" />
        <MetricTile label="SINGLE-TENANT CHURN EXPOSURE" value="-$2.7M Risk" sublabel="Client #312 Churn Probability: 34%" valueColor="#EF4444" />
        <MetricTile label="HEDGING STRATEGY STATUS" value="DISPATCHED" sublabel="Automated Tier Rebalancing Playbook Active" valueColor="#10B981" />
      </div>

      {/* Top Accounts Concentration Breakdown */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Top Customer Revenue Concentration Matrix</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Boardroom Exposure Audit</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {customerRisks.map((c, idx) => (
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
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{c.customerName}</span>
                  <Badge variant={c.riskLevel.startsWith('CRITICAL') ? 'rose' : 'amber'} size="sm">
                    {c.riskLevel}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  ARR Share: <strong style={{ color: '#EF4444' }}>{c.arrShare}</strong> • Renewal: {c.contractRenewal} • Health: <strong style={{ color: '#10B981' }}>{c.healthScore}</strong>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Button variant="danger" size="sm">
                  Deploy Retention Hedge Playbook
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
