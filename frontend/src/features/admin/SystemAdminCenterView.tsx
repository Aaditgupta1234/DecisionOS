import React, { useState } from 'react';
import { Settings, Users, Key, ShieldCheck, Activity, Database, DollarSign, CheckCircle2, ToggleLeft, ToggleRight } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';
import { useTenantStore } from '../../store/useTenantStore';
import { useFeatureFlagsStore } from '../../store/useFeatureFlagsStore';
import { UserRole } from '../../config/permissionsConfig';

export const SystemAdminCenterView: React.FC = () => {
  const { activeOrg, userRole, setUserRole } = useTenantStore();
  const { ENABLE_QUERY_DEVTOOLS, toggleFlag } = useFeatureFlagsStore();
  const [apiKeyCreated, setApiKeyCreated] = useState(false);

  const users = [
    { id: 'usr-1', name: 'Alexander Vance', email: 'a.vance@apexgroup.com', role: 'ADMIN' as UserRole, status: 'ACTIVE' },
    { id: 'usr-2', name: 'Elena Rostova', email: 'e.rostova@apexgroup.com', role: 'EXECUTIVE' as UserRole, status: 'ACTIVE' },
    { id: 'usr-3', name: 'Marcus Sterling', email: 'm.sterling@apexgroup.com', role: 'ANALYST' as UserRole, status: 'ACTIVE' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#64748B', fontWeight: 800 }}>
            Multi-Tenant SaaS Administration & RBAC
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            System Administration & SaaS Readiness Center
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Active Simulated Role:</span>
          <select
            value={userRole}
            onChange={(e) => setUserRole(e.target.value as UserRole)}
            style={{
              background: '#090D14',
              border: '1px solid #38BDF8',
              color: '#38BDF8',
              padding: '6px 12px',
              borderRadius: '8px',
              fontWeight: 800,
              fontSize: '0.8rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            <option value="ADMIN">ADMIN</option>
            <option value="EXECUTIVE">EXECUTIVE</option>
            <option value="ANALYST">ANALYST</option>
            <option value="VIEWER">VIEWER</option>
          </select>
        </div>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TENANT PLAN TIER" value="Enterprise Pro" sublabel="Unlimited Workspaces & Playbooks" valueColor="#38BDF8" />
        <MetricTile label="TOTAL ACTIVE USERS" value="18 Seats" sublabel="Role-Based Access Guarded" valueColor="#FFFFFF" />
        <MetricTile label="MONTHLY AI INFERENCE COST" value="$28.40" sublabel="Avg: $0.002 per Reasoning Trace" valueColor="#10B981" />
        <MetricTile label="SYSTEM UPTIME (SLA)" value="99.98%" sublabel="Zero Platform Outages" valueColor="#A855F7" />
      </div>

      {/* User Management & RBAC */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>User Directory & Permission Matrix</span>
          <Button variant="secondary" size="sm">
            Invite Enterprise Member
          </Button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {users.map((u) => (
            <div
              key={u.id}
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
              <div>
                <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>{u.name}</div>
                <div style={{ fontSize: '0.74rem', color: '#64748B' }}>{u.email}</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Badge variant={u.role === 'ADMIN' ? 'purple' : u.role === 'EXECUTIVE' ? 'emerald' : 'sky'} size="sm">
                  {u.role}
                </Badge>
                <Badge variant="emerald" size="sm">
                  {u.status}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Developer & Admin Settings */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Admin DevTools & API Keys</span>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '8px' }}>
          <div>
            <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#FFFFFF' }}>TanStack Query DevTools (Admin Only)</div>
            <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Enable live cache inspection and query freshness telemetry</div>
          </div>
          <button
            onClick={() => toggleFlag('ENABLE_QUERY_DEVTOOLS')}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: ENABLE_QUERY_DEVTOOLS ? '#10B981' : '#64748B' }}
          >
            {ENABLE_QUERY_DEVTOOLS ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '8px' }}>
          <div>
            <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#FFFFFF' }}>Enterprise API Keys (v1.0 REST)</div>
            <div style={{ fontSize: '0.74rem', color: '#64748B' }}>Provision secret tokens for external CRM & ERP system integration</div>
          </div>
          <Button variant="secondary" size="sm" icon={<Key size={14} />} onClick={() => setApiKeyCreated(true)}>
            Generate API Key
          </Button>
        </div>

        {apiKeyCreated && (
          <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '12px 16px', borderRadius: '8px', fontSize: '0.8rem', color: '#10B981', fontFamily: 'monospace' }}>
            New Key Generated: <strong>dos_live_8f7b2c9e10a48d39e271a06f</strong> (Saved to audit registry)
          </div>
        )}
      </Card>
    </div>
  );
};
