import React from 'react';
import { ShieldCheck, CheckCircle2, Lock, FileText, AlertTriangle, Key, ShieldAlert, Layers } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const SecurityCenterView: React.FC = () => {
  const controls = [
    { name: 'End-to-End TLS 1.3 Encryption in Transit', framework: 'SOC2 / ISO 27001', status: 'ENFORCED', score: '100%' },
    { name: 'AES-256 Multi-Tenant Column-Level Storage Encryption', framework: 'SOC2 / HIPAA', status: 'ENFORCED', score: '100%' },
    { name: 'Zero-Trust RBAC & Fine-Grained Permission Matrix', framework: 'SOC2 / GDPR', status: 'ENFORCED', score: '100%' },
    { name: 'Continuous Dependency Vulnerability Scanning', framework: 'SOC2 / ISO 27001', status: 'ENFORCED', score: '100%' },
    { name: 'Immutable Audit Log Storage with SHA-256 Hashing', framework: 'SOC2 / ISO 27001', status: 'ENFORCED', score: '100%' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Enterprise Security Hardening & Compliance
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Production Security & SOC2 Compliance Center
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="OVERALL SECURITY SCORE" value="98.4 / 100" sublabel="Grade A+ Certified" valueColor="#10B981" />
        <MetricTile label="SOC2 TYPE II CONTROLS" value="114 / 114" sublabel="100% Passed Continuous Audits" valueColor="#38BDF8" />
        <MetricTile label="THREAT EVENTS (PAST 24H)" value="0 Incidents" sublabel="Zero Access Violations" valueColor="#A855F7" />
        <MetricTile label="GDPR & ISO 27001 STATUS" value="COMPLIANT" sublabel="Cryptographically Audited" valueColor="#F59E0B" />
      </div>

      {/* Security Controls Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Active Enterprise Security Controls</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>SOC2 Type II Continuous Verification</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {controls.map((c, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '8px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <ShieldCheck size={16} color="#10B981" />
                  <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>{c.name}</span>
                </div>
                <div style={{ fontSize: '0.74rem', color: '#64748B', marginTop: '4px' }}>
                  Frameworks: {c.framework}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Badge variant="emerald" size="sm">
                  {c.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
