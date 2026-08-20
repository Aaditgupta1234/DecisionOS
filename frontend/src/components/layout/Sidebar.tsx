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
        backgroundColor: '#06080D',
        borderRight: '1px solid #14171E',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        flexShrink: 0,
      }}
    >
      {/* Brand Header */}
      <NavLink
        to="/"
        style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '0 16px',
          borderBottom: '1px solid #14171E',
          textDecoration: 'none',
          cursor: 'pointer',
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
            boxShadow: '0 0 14px rgba(56, 189, 248, 0.35)',
          }}
        >
          <ShieldCheck size={16} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 900, fontSize: '0.94rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '4px', letterSpacing: '-0.02em' }}>
            Decision<span style={{ color: '#38BDF8' }}>OS</span>
            <span style={{ fontSize: '0.65rem', padding: '1px 4px', borderRadius: '3px', background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', fontWeight: 800 }}>v1.0</span>
          </div>
          <div style={{ fontSize: '0.65rem', color: '#64748B', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {activeOrg.name}
          </div>
        </div>
      </NavLink>

      {/* Quick Search Button (Ctrl+K) */}
      <div style={{ padding: '10px 12px 6px 12px' }}>
        <button
          onClick={onOpenSearch}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 10px',
            background: '#080A0F',
            border: '1px solid #14171E',
            borderRadius: '8px',
            color: '#94A3B8',
            fontSize: '0.78rem',
            cursor: 'pointer',
            transition: 'border-color 0.15s ease',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Command size={13} color="#38BDF8" />
            Quick Command
          </span>
          <kbd style={{ fontSize: '0.65rem', background: '#040507', border: '1px solid #14171E', padding: '2px 5px', borderRadius: '4px', color: '#64748B' }}>
            Ctrl+K
          </kbd>
        </button>
      </div>

      {/* Navigation Links (21 Core Modules) */}
      <nav style={{ flex: 1, padding: '8px 10px', overflowY: 'auto' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '3px', padding: 0, margin: 0 }}>
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
                    padding: '8px 10px',
                    borderRadius: '8px',
                    color: isActive ? '#FFFFFF' : '#94A3B8',
                    backgroundColor: isActive ? 'rgba(56, 189, 248, 0.08)' : 'transparent',
                    border: isActive ? '1px solid rgba(56, 189, 248, 0.25)' : '1px solid transparent',
                    borderLeft: isActive ? '3px solid #38BDF8' : '1px solid transparent',
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
                          padding: '1px 5px',
                          borderRadius: '4px',
                          backgroundColor: 'rgba(56, 189, 248, 0.12)',
                          color: item.badgeColor || '#38BDF8',
                          border: `1px solid ${item.badgeColor || 'rgba(56, 189, 248, 0.25)'}`,
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
          borderTop: '1px solid #14171E',
          background: '#06080D',
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
              boxShadow: healthStatus === 'connected' ? '0 0 8px #10B981' : 'none',
            }}
          />
          <span style={{ fontWeight: 600 }}>{activeWorkspace.region}</span>
        </div>
        <span style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>v1.0 SaaS</span>
      </div>
    </aside>
  );
};
