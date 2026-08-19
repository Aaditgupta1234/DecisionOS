import React from 'react';
import { NavLink } from 'react-router-dom';
import { ShieldCheck, Command } from 'lucide-react';
import { routesConfig } from '../../config/routesConfig';
import { useTenantStore } from '../../store/useTenantStore';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';

interface SidebarProps {
  onOpenSearch?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenSearch }) => {
  const { status: healthStatus } = useBackendHealth();
  const { activeOrg, activeWorkspace } = useTenantStore();

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: '#090D14',
        borderRight: '1px solid #1E293B',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        flexShrink: 0,
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '0 16px',
          borderBottom: '1px solid #1E293B',
        }}
      >
        <div
          style={{
            width: '28px',
            height: '28px',
            borderRadius: '6px',
            background: 'linear-gradient(135deg, #1D4ED8, #0284C7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            boxShadow: '0 0 12px rgba(56, 189, 248, 0.3)',
          }}
        >
          <ShieldCheck size={16} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 800, fontSize: '0.92rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '4px' }}>
            Decision<span style={{ color: '#38BDF8' }}>OS</span>
            <span style={{ fontSize: '0.65rem', padding: '1px 4px', borderRadius: '3px', background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>v1.0</span>
          </div>
          <div style={{ fontSize: '0.65rem', color: '#64748B', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {activeOrg.name}
          </div>
        </div>
      </div>

      {/* Quick Search Button (Ctrl+K) */}
      <div style={{ padding: '10px 12px 4px 12px' }}>
        <button
          onClick={onOpenSearch}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '7px 10px',
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid #1E293B',
            borderRadius: '6px',
            color: '#94A3B8',
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Command size={13} color="#38BDF8" />
            Quick Command
          </span>
          <kbd style={{ fontSize: '0.65rem', background: '#090D14', border: '1px solid #334155', padding: '1px 4px', borderRadius: '3px' }}>
            Ctrl+K
          </kbd>
        </button>
      </div>

      {/* Navigation Links (21 Core Modules) */}
      <nav style={{ flex: 1, padding: '10px 10px', overflowY: 'auto' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '2px', padding: 0, margin: 0 }}>
          {routesConfig.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '7px 10px',
                    borderRadius: '6px',
                    color: isActive ? '#FFFFFF' : '#94A3B8',
                    backgroundColor: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                    borderLeft: isActive ? '3px solid #38BDF8' : '3px solid transparent',
                    fontWeight: isActive ? 700 : 500,
                    fontSize: '0.82rem',
                    transition: 'all 0.15s ease',
                    textDecoration: 'none',
                  })}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                    <Icon size={15} style={{ opacity: 0.9, flexShrink: 0 }} />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {item.title}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    {item.shortcut && (
                      <span style={{ fontSize: '0.6rem', color: '#475569', fontFamily: 'monospace' }}>
                        {item.shortcut}
                      </span>
                    )}
                    {item.badge && (
                      <span
                        style={{
                          fontSize: '0.6rem',
                          fontWeight: 800,
                          padding: '1px 4px',
                          borderRadius: '3px',
                          backgroundColor: 'rgba(56, 189, 248, 0.15)',
                          color: item.badgeColor || '#38BDF8',
                          border: `1px solid ${item.badgeColor || 'rgba(56, 189, 248, 0.3)'}`,
                        }}
                      >
                        {item.badge}
                      </span>
                    )}
                  </div>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Backend & Workspace Health Footer */}
      <div
        style={{
          padding: '12px 14px',
          borderTop: '1px solid #1E293B',
          background: 'rgba(15, 23, 42, 0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: '#94A3B8' }}>
          <span
            style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: healthStatus === 'connected' ? '#10B981' : '#F59E0B',
              boxShadow: healthStatus === 'connected' ? '0 0 6px #10B981' : 'none',
            }}
          />
          <span style={{ fontWeight: 600 }}>{activeWorkspace.region}</span>
        </div>
        <span style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>v1.0 SaaS</span>
      </div>
    </aside>
  );
};
