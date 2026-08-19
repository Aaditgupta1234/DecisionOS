import React, { useState } from 'react';
import { Database, RefreshCw, CheckCircle2, ArrowRight, ShieldCheck, Activity, Layers, Play } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const IntegrationsCenterView: React.FC = () => {
  const [syncingId, setSyncingId] = useState<string | null>(null);

  const connectors = [
    { id: 'conn-salesforce', name: 'Salesforce CRM Enterprise', type: 'CRM', status: 'CONNECTED', records: '42,100 records', syncFreq: '15m Delta', health: '99.9%', category: 'Revenue & Accounts' },
    { id: 'conn-sap', name: 'SAP S/4HANA ERP', type: 'ERP', status: 'CONNECTED', records: '182,400 records', syncFreq: 'Hourly Batch', health: '99.7%', category: 'Financials & Supply Chain' },
    { id: 'conn-jira', name: 'Jira Software Enterprise', type: 'TICKETING', status: 'CONNECTED', records: '8,920 epics', syncFreq: 'Realtime Webhook', health: '100.0%', category: 'Initiative Execution' },
    { id: 'conn-servicenow', name: 'ServiceNow ITSM', type: 'ITSM', status: 'CONNECTED', records: '14,500 incidents', syncFreq: '5m Polling', health: '99.8%', category: 'SLA Monitoring' },
    { id: 'conn-slack', name: 'Slack Enterprise Grid', type: 'MESSAGING', status: 'CONNECTED', records: '1,200 alerts', syncFreq: 'Outbound Hook', health: '100.0%', category: 'Executive Delivery' },
    { id: 'conn-teams', name: 'Microsoft Teams', type: 'MESSAGING', status: 'CONNECTED', records: '840 briefs', syncFreq: 'Outbound Hook', health: '100.0%', category: 'Executive Delivery' },
  ];

  const handleSync = (id: string) => {
    setSyncingId(id);
    setTimeout(() => setSyncingId(null), 1500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Enterprise API & Connector Ecosystem
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Integrations & Data Connectors
          </h1>
        </div>

        <Button variant="primary" size="sm">
          + Add Enterprise Connector
        </Button>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="CONNECTED ENTERPRISE SYSTEMS" value="6 Active" sublabel="Zero Connection Interruptions" valueColor="#10B981" />
        <MetricTile label="TOTAL SYNCHRONIZED RECORDS" value="249,960" sublabel="Ingested across Salesforce, SAP, Jira" valueColor="#38BDF8" />
        <MetricTile label="AVERAGE SYNC HEALTH" value="99.9%" sublabel="Pydantic Schema Conformance" valueColor="#A855F7" />
        <MetricTile label="WEBHOOK THROUGHPUT" value="120 req/s" sublabel="HMAC SHA-256 Verified" valueColor="#F59E0B" />
      </div>

      {/* Connectors Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Managed Integration Connectors</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Bi-Directional Telemetry Stream</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {connectors.map((c) => (
            <div
              key={c.id}
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
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{c.name}</span>
                  <Badge variant="emerald" size="sm">
                    {c.status}
                  </Badge>
                  <span style={{ fontSize: '0.72rem', color: '#64748B' }}>{c.category}</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Records: <strong style={{ color: '#FFFFFF' }}>{c.records}</strong> • Frequency: {c.syncFreq} • Health: <strong style={{ color: '#10B981' }}>{c.health}</strong>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<RefreshCw size={12} className={syncingId === c.id ? 'animate-spin' : ''} />}
                  onClick={() => handleSync(c.id)}
                  disabled={syncingId === c.id}
                >
                  {syncingId === c.id ? 'Syncing...' : 'Sync Now'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
