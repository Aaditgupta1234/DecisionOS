import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Activity,
  AlertTriangle,
  GitMerge,
  CheckCircle2,
  Sparkles,
  MessageSquare,
  Database,
  ShieldCheck,
  FileText,
  History,
} from 'lucide-react';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';

export const Sidebar: React.FC = () => {
  const { status: healthStatus } = useBackendHealth();

  const navItems = [
    { to: '/dashboard', label: 'Command Center', icon: LayoutDashboard },
    { to: '/datasets', label: 'Datasets', icon: Database },
    { to: '/metrics', label: 'KPI Performance', icon: Activity },
    { to: '/diagnostics', label: 'Diagnostic Findings', icon: AlertTriangle },
    { to: '/root-causes', label: 'Root Causes', icon: GitMerge },
    { to: '/recommendations', label: 'Recommendations', icon: CheckCircle2 },
    { to: '/reports', label: 'Executive Intelligence', icon: FileText },
    { to: '/history', label: 'Analysis History', icon: History },
    { to: '/ai-insights', label: 'AI Strategic Narrative', icon: Sparkles, badge: 'AI' },
    { to: '/chat', label: 'AI Chat Analyst', icon: MessageSquare, badge: 'AI' },
  ];

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-subtle)',
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
          padding: '0 20px',
          borderBottom: '1px solid var(--border-subtle)',
        }}
      >
        <div
          style={{
            width: '30px',
            height: '30px',
            borderRadius: 'var(--radius-sm)',
            background: 'linear-gradient(135deg, #1D4ED8, #0284C7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            boxShadow: '0 0 12px rgba(56, 189, 248, 0.3)',
          }}
        >
          <ShieldCheck size={18} />
        </div>
        <div>
          <span style={{ fontWeight: 800, fontSize: '1rem', letterSpacing: '-0.02em', color: '#fff' }}>
            Decision<span style={{ color: '#38BDF8' }}>OS</span>
          </span>
          <span
            style={{
              display: 'block',
              fontSize: '0.66rem',
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              fontWeight: 600,
            }}
          >
            Executive SaaS Platform
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: '14px 10px', overflowY: 'auto' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '3px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                    backgroundColor: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                    borderLeft: isActive ? '3px solid #38BDF8' : '3px solid transparent',
                    fontWeight: isActive ? 700 : 500,
                    fontSize: '0.85rem',
                    transition: 'all var(--transition-fast)',
                    textDecoration: 'none',
                  })}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Icon size={16} style={{ opacity: 0.9 }} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span
                      style={{
                        fontSize: '0.62rem',
                        fontWeight: 700,
                        padding: '1px 5px',
                        borderRadius: '4px',
                        backgroundColor: 'rgba(56, 189, 248, 0.15)',
                        color: '#38BDF8',
                        border: '1px solid rgba(56, 189, 248, 0.3)',
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Platform Backend Connectivity Status Footer */}
      <div
        style={{
          padding: '12px 18px',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: '0.75rem',
          color: 'var(--text-dim)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span>v7.0 SaaS Platform</span>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '5px',
          color: healthStatus === 'connected' ? '#10B981' : '#EF4444',
          fontWeight: 600,
          fontSize: '11px',
        }}>
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: healthStatus === 'connected' ? '#10B981' : '#EF4444',
            }}
          />
          {healthStatus === 'connected' ? 'Connected' : 'Offline'}
        </span>
      </div>
    </aside>
  );
};
