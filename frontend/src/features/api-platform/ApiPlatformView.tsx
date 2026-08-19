import React, { useState } from 'react';
import { Key, ShieldCheck, CheckCircle2, Code2, Globe, ArrowRight, Copy } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const ApiPlatformView: React.FC = () => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const keys = [
    { id: 'key-01', name: 'Production ERP Data Sync', prefix: 'dos_live_8f7b39a2...', scopes: 'read:kpis, write:scenarios', quota: '50,000 req/day', status: 'ACTIVE', created: 'Jan 15, 2026' },
    { id: 'key-02', name: 'Executive Mobile Portal', prefix: 'dos_live_3c2a91e4...', scopes: 'read:kpis, read:diagnostics', quota: '10,000 req/day', status: 'ACTIVE', created: 'Feb 20, 2026' },
  ];

  const endpoints = [
    { path: '/api/v1/public/kpis', method: 'GET', scope: 'read:kpis', desc: 'Access live governed enterprise KPIs and metrics' },
    { path: '/api/v1/public/diagnostics', method: 'GET', scope: 'read:diagnostics', desc: 'Query active causal findings, anomalies, and root causes' },
    { path: '/api/v1/public/scenarios/simulate', method: 'POST', scope: 'write:scenarios', desc: 'Trigger Digital Twin simulations programmatically' },
    { path: '/api/v1/public/decisions', method: 'POST', scope: 'admin:decisions', desc: 'Submit and audit executive decisions in Governance Registry' },
  ];

  const handleCopy = (id: string) => {
    setCopiedKey(id);
    setTimeout(() => setCopiedKey(null), 1500);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
            Enterprise Developer Gateway & SDK
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Public API Platform & Ecosystem
          </h1>
        </div>

        <Button variant="primary" size="sm">
          + Generate New API Key
        </Button>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="ACTIVE PUBLIC API KEYS" value="8 Keys" sublabel="Scoped RBAC Permissions" valueColor="#F59E0B" />
        <MetricTile label="DAILY REQUESTS SERVED" value="41,290" sublabel="Zero Rate Limit Violations" valueColor="#10B981" />
        <MetricTile label="AVERAGE GATEWAY LATENCY" value="28ms" sublabel="Global Edge Distribution" valueColor="#38BDF8" />
        <MetricTile label="REST SPECIFICATION" value="OpenAPI 3.1" sublabel="Full TypeScript & Python SDKs" valueColor="#A855F7" />
      </div>

      {/* API Keys Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Provisioned API Keys</span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {keys.map((k) => (
            <div
              key={k.id}
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
                  <Key size={16} color="#F59E0B" />
                  <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF' }}>{k.name}</span>
                  <Badge variant="emerald" size="sm">
                    {k.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Token: <code style={{ color: '#38BDF8' }}>{k.prefix}</code> • Scopes: {k.scopes} • Quota: {k.quota}
                </div>
              </div>

              <Button
                variant="secondary"
                size="sm"
                icon={<Copy size={12} />}
                onClick={() => handleCopy(k.id)}
              >
                {copiedKey === k.id ? 'Copied!' : 'Copy Key'}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Endpoints Catalog */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Public REST Endpoints (/api/v1/public/*)</span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {endpoints.map((e, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '8px',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '10px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '0.76rem', fontWeight: 900, color: e.method === 'GET' ? '#10B981' : '#38BDF8', padding: '3px 8px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '4px' }}>
                  {e.method}
                </span>
                <code style={{ fontSize: '0.84rem', color: '#FFFFFF' }}>{e.path}</code>
                <span style={{ fontSize: '0.78rem', color: '#64748B' }}>{e.desc}</span>
              </div>
              <Badge variant="purple" size="sm">
                {e.scope}
              </Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
