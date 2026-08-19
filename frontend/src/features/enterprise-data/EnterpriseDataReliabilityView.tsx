import React from 'react';
import { Database, ShieldCheck, CheckCircle2, Activity, Filter, Layers, Clock } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const EnterpriseDataReliabilityView: React.FC = () => {
  const sources = [
    { id: 'src-sf', name: 'Salesforce CRM Pipeline', freshness: '2m ago', completeness: '100.0%', accuracy: '99.8%', score: '99.8', records: '42,100', status: 'HEALTHY' },
    { id: 'src-sap', name: 'SAP S/4HANA ERP Ledger', freshness: '12m ago', completeness: '100.0%', accuracy: '99.2%', score: '99.2', records: '182,400', status: 'HEALTHY' },
    { id: 'src-telemetry', name: 'Live Courier Telemetry Stream', freshness: 'Realtime (4s)', completeness: '100.0%', accuracy: '100.0%', score: '100.0', records: '1,420,890', status: 'HEALTHY' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Executive Data Trust & Provenance Layer
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Enterprise Data Reliability & Quality Center
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="COMPOSITE DATA QUALITY SCORE" value="99.4%" sublabel="Grade A+ Enterprise Certified" valueColor="#10B981" />
        <MetricTile label="DATA FRESHNESS ENVELOPE" value="< 5 mins" sublabel="Across All Enterprise Connectors" valueColor="#38BDF8" />
        <MetricTile label="SCHEMA MAPPING ACCURACY" value="99.4%" sublabel="Zero Broken Telemetry Pipelines" valueColor="#A855F7" />
        <MetricTile label="AUDITED RECORDS (24H)" value="1,645,390" sublabel="SHA-256 Verified Lineage Hash" valueColor="#F59E0B" />
      </div>

      {/* Sources Quality Breakdown */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Ingested Data Sources & Fidelity Ratings</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Audited Lineage</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {sources.map((s) => (
            <div
              key={s.id}
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
                  <Database size={16} color="#10B981" />
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{s.name}</span>
                  <Badge variant="emerald" size="sm">
                    {s.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Freshness: <strong style={{ color: '#38BDF8' }}>{s.freshness}</strong> • Completeness: {s.completeness} • Mapping Accuracy: {s.accuracy} • Records: {s.records}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 900, color: '#10B981', padding: '6px 14px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px' }}>
                  Quality: {s.score}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
