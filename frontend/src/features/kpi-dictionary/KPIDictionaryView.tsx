import React, { useState } from 'react';
import { BookOpen, Search, Filter, ShieldCheck, Database, Layers } from 'lucide-react';
import { Card, Badge, MetricTile } from '../../design-system';
import { KPIDefinition } from '../../types/KPIDefinition';

export const KPIDictionaryView: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const kpis: KPIDefinition[] = [
    {
      id: 'kpi-01',
      metricName: 'Annual Recurring Revenue (ARR)',
      category: 'REVENUE',
      formula: 'SUM(Active Subscription Contracts * 12) + Net Expansion',
      owner: 'VP Strategic Finance',
      ownerRole: 'CFO',
      dataSource: 'Stripe Billing & Salesforce CRM',
      refreshFrequency: 'REALTIME',
      unit: '$ USD',
      targetValue: 14000000,
      currentValue: 12400000,
      description: 'Normalized annual run-rate of recurring contracted software subscription revenue.',
      version: 'v2.4',
      isBoardMetric: true,
    },
    {
      id: 'kpi-02',
      metricName: 'Customer Retention Rate',
      category: 'RETENTION',
      formula: '((Active Customers End - Acquired) / Active Customers Start) * 100',
      owner: 'Head of Customer Success',
      ownerRole: 'COO',
      dataSource: 'Telemetry Event Stream & Data Warehouse',
      refreshFrequency: 'DAILY',
      unit: '%',
      targetValue: 91.0,
      currentValue: 84.2,
      description: 'Trailing 90-day active customer account retention across all distribution corridors.',
      version: 'v3.1',
      isBoardMetric: true,
    },
    {
      id: 'kpi-03',
      metricName: 'Courier Delivery Latency',
      category: 'OPERATIONS',
      formula: 'AVG(Delivery Timestamp - Ingestion Timestamp) in Business Days',
      owner: 'VP Logistics Operations',
      ownerRole: 'VP Operations',
      dataSource: 'Regional Carrier Telemetry Hub',
      refreshFrequency: 'HOURLY',
      unit: 'Days',
      targetValue: 3.0,
      currentValue: 3.4,
      description: 'End-to-end parcel routing transit latency from fulfillment scan to customer receipt.',
      version: 'v1.8',
      isBoardMetric: false,
    },
  ];

  const filtered = kpis.filter(
    (k) =>
      k.metricName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.formula.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.owner.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
            Enterprise Metric Governance & Formula Lineage
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise KPI Dictionary & Metadata Registry
          </h1>
        </div>

        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#090D14', border: '1px solid #1E293B', borderRadius: '8px', padding: '6px 12px' }}>
          <Search size={16} color="#64748B" />
          <input
            type="text"
            placeholder="Search formulas or owners..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#FFFFFF', outline: 'none', fontSize: '0.82rem' }}
          />
        </div>
      </div>

      {/* Hero Metric Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL REGISTERED METRICS" value="32 KPIs" sublabel="100% Governed & Versioned" valueColor="#FFFFFF" />
        <MetricTile label="BOARDROOM METRICS" value="12 KPIs" sublabel="Enforced in Executive Reports" valueColor="#F59E0B" />
        <MetricTile label="DATA PROVENANCE COVERAGE" value="100%" sublabel="Full Source Lineage Audited" valueColor="#10B981" />
        <MetricTile label="FORMULA ACCURACY RATING" value="99.4%" sublabel="Automated Pydantic Schema Validation" valueColor="#38BDF8" />
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filtered.map((kpi) => (
          <Card key={kpi.id} style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFFFFF' }}>{kpi.metricName}</span>
                <Badge variant={kpi.category === 'REVENUE' ? 'emerald' : kpi.category === 'RETENTION' ? 'rose' : 'sky'} size="sm">
                  {kpi.category}
                </Badge>
                {kpi.isBoardMetric && (
                  <Badge variant="amber" size="sm">
                    BOARD METRIC
                  </Badge>
                )}
              </div>
              <span style={{ fontSize: '0.74rem', color: '#64748B' }}>Version: {kpi.version} • Refresh: {kpi.refreshFrequency}</span>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '10px 14px', borderRadius: '8px', fontSize: '0.8rem', color: '#38BDF8', fontFamily: 'monospace' }}>
              Formula: {kpi.formula}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px', fontSize: '0.76rem', color: '#94A3B8' }}>
              <div>Owner: <strong style={{ color: '#FFFFFF' }}>{kpi.owner}</strong> ({kpi.ownerRole}) • Source: {kpi.dataSource}</div>
              <div>Current: <strong style={{ color: '#10B981' }}>{kpi.currentValue} {kpi.unit}</strong> (Target: {kpi.targetValue} {kpi.unit})</div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
