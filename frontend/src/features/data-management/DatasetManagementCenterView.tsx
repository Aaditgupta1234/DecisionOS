import React from 'react';
import { Database, Upload, CheckCircle2, FileText, Activity, Layers, ArrowRight } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const DatasetManagementCenterView: React.FC = () => {
  const datasets = [
    {
      id: 'ds-01',
      name: 'Enterprise Telemetry Event Stream Q1-2026',
      rows: '1,420,890 events',
      kpisExtracted: '32 KPIs',
      status: 'VERIFIED_ACTIVE',
      validationRating: '100% (Zero Schema Violations)',
      ingestedAt: '2026-03-18 09:14 UTC',
    },
    {
      id: 'ds-02',
      name: 'Regional Courier Transit Logs & SLAs',
      rows: '842,100 records',
      kpisExtracted: '8 KPIs',
      status: 'VERIFIED_ACTIVE',
      validationRating: '99.8% (SOC2 Audited)',
      ingestedAt: '2026-03-17 14:22 UTC',
    },
    {
      id: 'ds-03',
      name: 'Stripe SaaS Billing & Customer Cohort Ledger',
      rows: '412,500 transactions',
      kpisExtracted: '12 KPIs',
      status: 'VERIFIED_ACTIVE',
      validationRating: '100% Clean',
      ingestedAt: '2026-03-15 18:40 UTC',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Enterprise Ingestion Pipeline & Schema Lineage
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Dataset Management & Telemetry Center
          </h1>
        </div>

        <Button variant="primary" size="sm" icon={<Upload size={14} />}>
          Upload New Enterprise Dataset
        </Button>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL INGESTED RECORDS" value="2.67M" sublabel="Live Continuous Ingestion Stream" valueColor="#10B981" />
        <MetricTile label="ACTIVE SCHEMAS MAPPED" value="32 KPIs" sublabel="Pydantic Validated & Versioned" valueColor="#38BDF8" />
        <MetricTile label="SCHEMA CONFORMANCE" value="99.9%" sublabel="Zero Broken Telemetry Pipelines" valueColor="#A855F7" />
        <MetricTile label="DATA PROVENANCE HASH" value="VERIFIED" sublabel="SHA-256 Verified Lineage" valueColor="#F59E0B" />
      </div>

      {/* Ingested Datasets Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Managed Telemetry Datasets</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Enterprise Source of Truth</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {datasets.map((d) => (
            <div
              key={d.id}
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
                  <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF' }}>{d.name}</span>
                  <Badge variant="emerald" size="sm">
                    {d.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Rows: <strong style={{ color: '#FFFFFF' }}>{d.rows}</strong> • KPIs: <strong style={{ color: '#38BDF8' }}>{d.kpisExtracted}</strong> • Conformance: {d.validationRating}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '0.74rem', color: '#64748B' }}>{d.ingestedAt}</span>
                <Button variant="secondary" size="sm">
                  View Schema Mapping
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
