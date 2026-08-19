import React, { useState } from 'react';
import { Settings, ShieldCheck, CheckCircle2, Globe, Palette, Clock, ToggleLeft, ToggleRight, Layers } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const EnterpriseAdministrationView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'BRANDING' | 'SECURITY' | 'RETENTION' | 'FLAGS'>('BRANDING');
  const [flags, setFlags] = useState({
    ENABLE_AUTONOMOUS_AGENTS: true,
    ENABLE_CAPITAL_ALLOCATION: true,
    ENABLE_WHITE_LABEL: true,
    ENABLE_PUBLIC_API: true,
    ENABLE_DIGITAL_TWIN: true,
  });

  const toggleFlag = (key: keyof typeof flags) => {
    setFlags((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
          Central Enterprise SaaS Configuration
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Enterprise Administration & System Console
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TENANT ORGANIZATION" value="Apex Global Group" sublabel="decisionos.apexgroup.com" valueColor="#38BDF8" />
        <MetricTile label="MFA SECURITY STATUS" value="ENFORCED" sublabel="Okta SAML 2.0 Single Sign-On" valueColor="#10B981" />
        <MetricTile label="DATA RETENTION POLICY" value="7 Years" sublabel="Immutable Audit Ledger" valueColor="#A855F7" />
        <MetricTile label="ACTIVE FEATURE FLAGS" value="5 / 5 Enabled" sublabel="Full Platform Capabilities" valueColor="#F59E0B" />
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', padding: '3px', width: 'fit-content' }}>
        <button
          onClick={() => setActiveTab('BRANDING')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'BRANDING' ? '#38BDF8' : 'transparent',
            color: activeTab === 'BRANDING' ? '#090D14' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          White-Label & Branding
        </button>
        <button
          onClick={() => setActiveTab('SECURITY')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'SECURITY' ? '#10B981' : 'transparent',
            color: activeTab === 'SECURITY' ? '#090D14' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          Security & SSO
        </button>
        <button
          onClick={() => setActiveTab('RETENTION')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'RETENTION' ? '#A855F7' : 'transparent',
            color: activeTab === 'RETENTION' ? '#FFFFFF' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          Data Retention Rules
        </button>
        <button
          onClick={() => setActiveTab('FLAGS')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'FLAGS' ? '#F59E0B' : 'transparent',
            color: activeTab === 'FLAGS' ? '#090D14' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          Feature Flags
        </button>
      </div>

      {activeTab === 'BRANDING' && (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Custom White-Label Portal Profile</span>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
              <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 700 }}>ORGANIZATION NAME</div>
              <div style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF', marginTop: '4px' }}>Apex Global Technologies Group</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
              <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 700 }}>CUSTOM DOMAIN</div>
              <div style={{ fontSize: '0.94rem', fontWeight: 800, color: '#38BDF8', marginTop: '4px' }}>decisionos.apexgroup.com</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '8px', border: '1px solid #1E293B' }}>
              <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 700 }}>PRIMARY BRAND COLOR</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                <div style={{ width: '16px', height: '16px', background: '#38BDF8', borderRadius: '4px' }} />
                <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>#38BDF8 (Sky Blue)</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'SECURITY' && (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Authentication & Security Configuration</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px 18px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong style={{ color: '#FFFFFF' }}>Okta SAML 2.0 Single Sign-On</strong>
                <div style={{ fontSize: '0.76rem', color: '#94A3B8' }}>Enforced for all internal corporate accounts</div>
              </div>
              <Badge variant="emerald" size="sm">ACTIVE</Badge>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px 18px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong style={{ color: '#FFFFFF' }}>SCIM 2.0 User & Group Directory Sync</strong>
                <div style={{ fontSize: '0.76rem', color: '#94A3B8' }}>Auto-provision roles and workspaces</div>
              </div>
              <Badge variant="emerald" size="sm">ENABLED</Badge>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'RETENTION' && (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Enterprise Data Lifecycle Rules</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px 18px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>Live Telemetry Stream</span>
              <span style={{ color: '#38BDF8', fontWeight: 800 }}>90 Days (Cold Storage Archive)</span>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px 18px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>Governance Decision Records</span>
              <span style={{ color: '#10B981', fontWeight: 800 }}>Permanent (Blockchain Hash Audited)</span>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px 18px', borderRadius: '8px', border: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>Board Meeting Presentation Decks</span>
              <span style={{ color: '#A855F7', fontWeight: 800 }}>Permanent (Executive Sign-Off)</span>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'FLAGS' && (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Platform Capabilities & Feature Toggles</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(flags).map(([key, val]) => (
              <div
                key={key}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  padding: '14px 18px',
                  borderRadius: '8px',
                  border: '1px solid #1E293B',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ color: '#FFFFFF', fontWeight: 700, fontFamily: 'monospace', fontSize: '0.84rem' }}>{key}</span>
                <button
                  onClick={() => toggleFlag(key as keyof typeof flags)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: val ? '#10B981' : '#64748B' }}
                >
                  {val ? <ToggleRight size={26} /> : <ToggleLeft size={26} />}
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
