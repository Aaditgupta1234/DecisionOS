import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  Command,
  LayoutDashboard,
  FileText,
  MessageSquare,
  Bot,
  Database,
  BookOpen,
  AlertTriangle,
  Lightbulb,
  GitMerge,
  PlayCircle,
  Target,
  DollarSign,
  ShieldAlert,
  Scale,
  Globe,
  TrendingUp,
  Activity,
  Layers,
  Key,
  Zap,
  Server,
  Settings,
  ChevronDown,
  ChevronRight,
} from 'lucide-react';
import { useTenantStore } from '../../store/useTenantStore';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';

interface SidebarProps {
  onOpenSearch?: () => void;
}

interface NavItem {
  path: string;
  title: string;
  icon: any;
  badge?: string;
}

interface NavGroup {
  id: string;
  title: string;
  items: NavItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenSearch }) => {
  const { status: healthStatus } = useBackendHealth();
  const { activeOrg, activeWorkspace } = useTenantStore();
  const location = useLocation();

  // 1. Always Visible Top-Level Core Modules
  const pinnedItems: NavItem[] = [
    { path: '/enterprise', title: 'Enterprise Command', icon: LayoutDashboard, badge: 'OS v1' },
    { path: '/boardroom', title: 'Executive Boardroom', icon: FileText, badge: 'BOARD' },
    { path: '/chat', title: 'AI Business Analyst', icon: MessageSquare, badge: 'ANALYST' },
    { path: '/decision-copilot', title: 'AI Decision Copilot', icon: Bot, badge: 'COPILOT' },
  ];

  // 2. The 5 Enterprise Platform Groups
  const navGroups: NavGroup[] = [
    {
      id: 'data-intel',
      title: 'Data & Intelligence',
      items: [
        { path: '/enterprise-data', title: 'Enterprise Data Hub', icon: Database, badge: 'DATA' },
        { path: '/kpi-dictionary', title: 'KPI Dictionary', icon: BookOpen, badge: 'DICT' },
        { path: '/diagnostics', title: 'Diagnostic Findings', icon: AlertTriangle, badge: 'FINDINGS' },
        { path: '/recommendations', title: 'Recommendations', icon: Lightbulb, badge: 'AI' },
        { path: '/knowledge-graph', title: 'Knowledge Graph DAG', icon: GitMerge, badge: 'GRAPH' },
      ],
    },
    {
      id: 'strategy-exec',
      title: 'Strategy & Execution',
      items: [
        { path: '/digital-twin', title: 'Digital Twin & Scenarios', icon: PlayCircle, badge: 'TWIN' },
        { path: '/strategy-execution', title: 'Strategy Execution', icon: Target, badge: 'VALUE' },
        { path: '/capital-allocation', title: 'Capital Allocation Studio', icon: DollarSign, badge: 'CAPITAL' },
        { path: '/reports', title: 'Executive Reports Studio', icon: FileText, badge: 'REPORTS' },
      ],
    },
    {
      id: 'governance-risk',
      title: 'Governance & Risk',
      items: [
        { path: '/risk-concentration', title: 'Risk Concentration Radar', icon: ShieldAlert, badge: 'RISK' },
        { path: '/governance', title: 'Decision Governance Registry', icon: Scale, badge: 'GOV' },
        { path: '/ai-governance', title: 'AI Usage Governance', icon: Bot, badge: 'AUDIT' },
        { path: '/security-center', title: 'Security & Compliance', icon: ShieldCheck, badge: 'SOC2' },
      ],
    },
    {
      id: 'enterprise-portfolio',
      title: 'Enterprise Portfolio',
      items: [
        { path: '/portfolio-rollup', title: 'Multi-Portfolio Rollup', icon: Globe, badge: 'PORTFOLIO' },
        { path: '/competitive-intel', title: 'Competitive Benchmarks', icon: TrendingUp, badge: 'INDEX' },
        { path: '/monitoring', title: 'Continuous Monitoring', icon: Activity, badge: 'LIVE' },
        { path: '/data-reliability', title: 'Data Reliability Center', icon: Database, badge: '99.4%' },
      ],
    },
    {
      id: 'platform-admin',
      title: 'Platform Admin',
      items: [
        { path: '/integrations', title: 'Enterprise Integrations', icon: Layers, badge: 'SYNC' },
        { path: '/api-platform', title: 'Enterprise API Platform', icon: Key, badge: 'API' },
        { path: '/agents', title: 'Autonomous Agents Hub', icon: Zap, badge: 'AGENTS' },
        { path: '/platform-ops', title: 'Platform Operations', icon: Server, badge: '99.98%' },
        { path: '/administration', title: 'Enterprise Administration', icon: Settings, badge: 'ADMIN' },
      ],
    },
  ];

  // Collapsible state for each category (all closed by default)
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({});

  const toggleGroup = (groupId: string) => {
    setOpenGroups((prev) => ({ ...prev, [groupId]: !prev[groupId] }));
  };

  const renderNavLink = (item: NavItem) => {
    const Icon = item.icon;
    return (
      <li key={item.path}>
        <NavLink
          to={item.path}
          style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '5px 8px',
            borderRadius: '6px',
            color: isActive ? '#FFFFFF' : '#94A3B8',
            backgroundColor: isActive ? 'rgba(255, 255, 255, 0.06)' : 'transparent',
            border: isActive ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid transparent',
            borderLeft: isActive ? '3px solid #FFFFFF' : '1px solid transparent',
            fontWeight: isActive ? 700 : 500,
            fontSize: '0.76rem',
            transition: 'all 0.15s ease',
            textDecoration: 'none',
          })}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '7px', minWidth: 0, flex: 1 }}>
            <Icon size={14} style={{ opacity: 0.9, flexShrink: 0 }} />
            <span
              title={item.title}
              style={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                fontSize: '0.76rem',
                letterSpacing: '-0.01em',
              }}
            >
              {item.title}
            </span>
          </div>
          {item.badge && (
            <span
              style={{
                fontSize: '0.54rem',
                fontWeight: 700,
                padding: '1px 5px',
                borderRadius: '3px',
                backgroundColor: '#0F172A',
                color: '#CBD5E1',
                border: '1px solid #334155',
                letterSpacing: '0.04em',
                flexShrink: 0,
                marginLeft: '4px',
              }}
            >
              {item.badge}
            </span>
          )}
        </NavLink>
      </li>
    );
  };

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: '#06080D',
        borderRight: '1px solid #161A22',
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
          borderBottom: '1px solid #161A22',
          textDecoration: 'none',
          cursor: 'pointer',
        }}
      >
        <div
          style={{
            width: '28px',
            height: '28px',
            borderRadius: '6px',
            background: '#11141B',
            border: '1px solid #1E232E',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
          }}
        >
          <ShieldCheck size={16} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 900, fontSize: '0.94rem', color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '4px', letterSpacing: '-0.02em' }}>
            Decision<span style={{ color: '#FFFFFF' }}>OS</span>
            <span style={{ fontSize: '0.62rem', padding: '1px 5px', borderRadius: '3px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', color: '#CBD5E1', fontWeight: 700 }}>v1.0</span>
          </div>
          <div style={{ fontSize: '0.65rem', color: '#64748B', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {activeOrg.name}
          </div>
        </div>
      </NavLink>

      {/* Quick Search Button (Ctrl+K) */}
      <div style={{ padding: '6px 10px 4px 10px' }}>
        <button
          onClick={onOpenSearch}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '6px 8px',
            background: '#080A0E',
            border: '1px solid #161A22',
            borderRadius: '6px',
            color: '#94A3B8',
            fontSize: '0.74rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <Command size={12} color="#CBD5E1" />
            Quick Command
          </span>
          <kbd style={{ fontSize: '0.62rem', background: '#040507', border: '1px solid #161A22', padding: '1px 4px', borderRadius: '3px', color: '#64748B' }}>
            Ctrl+K
          </kbd>
        </button>
      </div>

      {/* Navigation Links with Pinned Core & 5 Collapsible Groups */}
      <nav style={{ flex: 1, padding: '4px 8px', overflowY: 'auto' }}>
        
        {/* Pinned Top-Level Core Modules */}
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '2px', padding: 0, margin: '0 0 10px 0' }}>
          {pinnedItems.map((item) => renderNavLink(item))}
        </ul>

        {/* 5 Enterprise Collapsible Groups */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {navGroups.map((group) => {
            const isOpen = !!openGroups[group.id];
            const hasActiveChild = group.items.some((item) => item.path === location.pathname);

            return (
              <div key={group.id} style={{ display: 'flex', flexDirection: 'column' }}>
                {/* Group Header Button */}
                <button
                  onClick={() => toggleGroup(group.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    width: '100%',
                    padding: '4px 6px',
                    background: 'transparent',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    color: hasActiveChild ? '#CBD5E1' : '#64748B',
                    fontSize: '0.64rem',
                    fontWeight: 800,
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    textAlign: 'left',
                    transition: 'color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#FFFFFF')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = hasActiveChild ? '#CBD5E1' : '#64748B')}
                >
                  <span>{group.title}</span>
                  {isOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
                </button>

                {/* Group Items */}
                {isOpen && (
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '2px', padding: 0, margin: '2px 0 0 0' }}>
                    {group.items.map((item) => renderNavLink(item))}
                  </ul>
                )}
              </div>
            );
          })}
        </div>
      </nav>

      {/* Backend & Workspace Health Footer */}
      <div
        style={{
          padding: '10px 14px',
          borderTop: '1px solid #161A22',
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
export default Sidebar;

