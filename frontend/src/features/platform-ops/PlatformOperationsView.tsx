import React from 'react';
import { Activity, Server, Cpu, Database, CheckCircle2, ShieldCheck, GitCommit, Layers } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const PlatformOperationsView: React.FC = () => {
  const deployments = [
    { id: 'dep-live', version: 'v1.0.4-enterprise', commit: '7693095', status: 'HEALTHY', env: 'Production (us-east-1)', time: 'Today at 23:17 UTC' },
    { id: 'dep-prev', version: 'v1.0.3-enterprise', commit: '43f17be', status: 'SUPERSEDED', env: 'Production Archive', time: 'Today at 23:13 UTC' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Live SaaS Infrastructure & Operations
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Platform Operations & System Health Center
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="SYSTEM UPTIME SLA" value="99.98%" sublabel="Exceeding 99.9% Enterprise Target" valueColor="#10B981" />
        <MetricTile label="GATEWAY P95 LATENCY" value="142ms" sublabel="P99: 224ms Envelope" valueColor="#38BDF8" />
        <MetricTile label="ACTIVE WORKER THREADS" value="16 Threads" sublabel="Zero Queue Backlog" valueColor="#A855F7" />
        <MetricTile label="RELEASE VERSION" value="v1.0.4" sublabel="Commit: 7693095 (Clean)" valueColor="#F59E0B" />
      </div>

      {/* Deployments & Subsystems */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {/* Subsystems Health */}
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Subsystem Health Status</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Server size={16} color="#10B981" />
                <span style={{ color: '#FFFFFF', fontWeight: 700, fontSize: '0.86rem' }}>FastAPI Gateway Cluster</span>
              </div>
              <Badge variant="emerald" size="sm">0.00% Errors</Badge>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Database size={16} color="#38BDF8" />
                <span style={{ color: '#FFFFFF', fontWeight: 700, fontSize: '0.86rem' }}>PostgreSQL Database Pool</span>
              </div>
              <Badge variant="sky" size="sm">12 / 100 Conn</Badge>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={16} color="#A855F7" />
                <span style={{ color: '#FFFFFF', fontWeight: 700, fontSize: '0.86rem' }}>Redis & Celery Workers</span>
              </div>
              <Badge variant="purple" size="sm">4 Nodes Idle</Badge>
            </div>
          </div>
        </Card>

        {/* Deployment History */}
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Recent Production Releases</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {deployments.map((d) => (
              <div
                key={d.id}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  padding: '14px 16px',
                  borderRadius: '8px',
                  border: '1px solid #1E293B',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <GitCommit size={16} color="#10B981" />
                    <strong style={{ color: '#FFFFFF', fontSize: '0.9rem' }}>{d.version}</strong>
                    <Badge variant={d.status === 'HEALTHY' ? 'emerald' : 'slate'} size="sm">
                      {d.status}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#64748B', marginTop: '2px' }}>
                    Commit: <code style={{ color: '#38BDF8' }}>{d.commit}</code> • {d.env}
                  </div>
                </div>
                <span style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{d.time}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
