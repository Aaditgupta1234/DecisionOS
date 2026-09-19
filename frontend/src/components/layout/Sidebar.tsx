import React, { useState, useEffect } from 'react';
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
  ChevronLeft,
  PanelLeftClose,
  PanelLeftOpen,
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
  icon?: any;
  items: NavItem[];
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenSearch }) => {
  const { status: healthStatus } = useBackendHealth();
  const { activeOrg, activeWorkspace } = useTenantStore();
  const location = useLocation();

  // Sidebar Minimized / Collapsed State with LocalStorage Persistence
  const [isCollapsed, setIsCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem('decisionos_sidebar_collapsed') === 'true';
    } catch {
      return false;
    }
  });

  const toggleCollapsed = () => {
    setIsCollapsed((prev) => {
      const next = !prev;
      try {
        localStorage.setItem('decisionos_sidebar_collapsed', String(next));
      } catch {}
      return next;
    });
  };

  // Keyboard shortcut Ctrl+B or Cmd+B to toggle sidebar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b' && !e.shiftKey && !e.altKey) {
        e.preventDefault();
        toggleCollapsed();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // 1. Always Visible Top-Level Core Modules
  const pinnedItems: NavItem[] = [
    { path: '/enterprise', title: 'Enterprise Command', icon: LayoutDashboard, badge: 'OS v1' },
    { path: '/boardroom', title: 'Executive Boardroom', icon: FileText, badge: 'BOARD' },
    { path: '/chat', title: 'DEX Analyst', icon: MessageSquare, badge: 'ANALYST' },
    { path: '/decision-copilot', title: 'AI Decision Copilot', icon: Bot, badge: 'COPILOT' },
  ];

  // 2. The 5 Enterprise Platform Groups
  const navGroups: NavGroup[] = [
    {
      id: 'data-intel',
      title: 'Data & Intelligence',
      icon: Database,
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
      icon: Target,
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
      icon: ShieldAlert,
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
      icon: Globe,
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
      icon: Settings,
      items: [
        { path: '/integrations', title: 'Enterprise Integrations', icon: Layers, badge: 'SYNC' },
        { path: '/api-platform', title: 'Enterprise API Platform', icon: Key, badge: 'API' },
        { path: '/agents', title: 'Autonomous Agents Hub', icon: Zap, badge: 'AGENTS' },
        { path: '/platform-ops', title: 'Platform Operations', icon: Server, badge: '99.8%' },
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
          title={isCollapsed ? `${item.title} ${item.badge ? `(${item.badge})` : ''}` : undefined}
          style={({ isActive }) => ({
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'space-between',
            padding: isCollapsed ? '8px 0' : '5px 8px',
            borderRadius: '6px',
            color: isActive ? '#FFFFFF' : '#94A3B8',
            backgroundColor: isActive ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
            border: isActive ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid transparent',
            borderLeft: isActive ? '3px solid #FFFFFF' : '1px solid transparent',
            fontWeight: isActive ? 700 : 500,
            fontSize: '0.76rem',
            transition: 'all 0.15s ease',
            textDecoration: 'none',
            position: 'relative',
          })}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: isCollapsed ? '0' : '7px', minWidth: 0, justifyContent: isCollapsed ? 'center' : 'flex-start', width: isCollapsed ? '100%' : 'auto', flex: 1 }}>
            <Icon size={isCollapsed ? 16 : 14} style={{ opacity: 0.9, flexShrink: 0 }} />
            {!isCollapsed && (
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
            )}
          </div>
          {!isCollapsed && item.badge && (
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
        width: isCollapsed ? '58px' : '236px',
        backgroundColor: '#06080D',
        borderRight: '1px solid #161A22',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        flexShrink: 0,
        transition: 'width 0.22s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        zIndex: 40,
      }}
    >
      {/* Brand Header with Minimize / Expand Toggle Button */}
      <div
        style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          padding: isCollapsed ? '0 8px' : '0 12px 0 14px',
          borderBottom: '1px solid #161A22',
          boxSizing: 'border-box',
        }}
      >
        <NavLink
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            textDecoration: 'none',
            cursor: 'pointer',
            minWidth: 0,
            flex: isCollapsed ? 'none' : 1,
          }}
          title={isCollapsed ? `DecisionOS v1.0 (${activeOrg.name})` : undefined}
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
              flexShrink: 0,
            }}
          >
            <ShieldCheck size={16} />
          </div>

          {!isCollapsed && (
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 900, fontSize: '0.92rem', color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '4px', letterSpacing: '-0.02em' }}>
                Decision<span style={{ color: '#FFFFFF' }}>OS</span>
                <span style={{ fontSize: '0.60rem', padding: '1px 4px', borderRadius: '3px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)', color: '#CBD5E1', fontWeight: 700 }}>v1.0</span>
              </div>
              <div style={{ fontSize: '0.64rem', color: '#64748B', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {activeOrg.name}
              </div>
            </div>
          )}
        </NavLink>

        {/* Sidebar Minimize / Expand Toggle Button */}
        <button
          onClick={toggleCollapsed}
          title={isCollapsed ? 'Expand Sidebar (Ctrl+B)' : 'Minimize Sidebar (Ctrl+B)'}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: isCollapsed ? '32px' : '26px',
            height: isCollapsed ? '32px' : '26px',
            background: isCollapsed ? 'transparent' : 'rgba(255, 255, 255, 0.03)',
            border: isCollapsed ? 'none' : '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: '5px',
            color: '#94A3B8',
            cursor: 'pointer',
            padding: 0,
            transition: 'all 0.15s ease',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#FFFFFF';
            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = '#94A3B8';
            e.currentTarget.style.borderColor = isCollapsed ? 'transparent' : 'rgba(255, 255, 255, 0.08)';
            e.currentTarget.style.backgroundColor = isCollapsed ? 'transparent' : 'rgba(255, 255, 255, 0.03)';
          }}
        >
          {isCollapsed ? <PanelLeftOpen size={15} /> : <PanelLeftClose size={14} />}
        </button>
      </div>

      {/* Quick Search Button (Ctrl+K) */}
      <div style={{ padding: isCollapsed ? '6px 6px 4px 6px' : '6px 10px 4px 10px' }}>
        <button
          onClick={onOpenSearch}
          title="Quick Command Palette (Ctrl+K)"
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'space-between',
            padding: isCollapsed ? '7px 0' : '6px 8px',
            background: '#080A0E',
            border: '1px solid #161A22',
            borderRadius: '6px',
            color: '#94A3B8',
            fontSize: '0.74rem',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#334155';
            e.currentTarget.style.color = '#FFFFFF';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#161A22';
            e.currentTarget.style.color = '#94A3B8';
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <Command size={isCollapsed ? 15 : 12} color="#CBD5E1" />
            {!isCollapsed && 'Quick Command'}
          </span>
          {!isCollapsed && (
            <kbd style={{ fontSize: '0.62rem', background: '#040507', border: '1px solid #161A22', padding: '1px 4px', borderRadius: '3px', color: '#64748B' }}>
              Ctrl+K
            </kbd>
          )}
        </button>
      </div>

      {/* Navigation Links with Pinned Core & 5 Collapsible Groups */}
      <nav style={{ flex: 1, padding: isCollapsed ? '4px 6px' : '4px 8px', overflowY: 'auto', overflowX: 'hidden' }}>
        
        {/* Pinned Top-Level Core Modules */}
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '2px', padding: 0, margin: '0 0 10px 0' }}>
          {pinnedItems.map((item) => renderNavLink(item))}
        </ul>

        {/* Divider in Collapsed Mode */}
        {isCollapsed && (
          <div style={{ height: '1px', background: 'rgba(255, 255, 255, 0.06)', margin: '6px 4px 8px 4px' }} />
        )}

        {/* 5 Enterprise Collapsible Groups */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: isCollapsed ? '6px' : '8px' }}>
          {navGroups.map((group) => {
            const isOpen = isCollapsed ? true : !!openGroups[group.id];
            const hasActiveChild = group.items.some((item) => item.path === location.pathname);

            return (
              <div key={group.id} style={{ display: 'flex', flexDirection: 'column' }}>
                {/* Group Header Button (Expanded Mode only) */}
                {!isCollapsed ? (
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
                ) : null}

                {/* Group Items */}
                {isOpen && (
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '2px', padding: 0, margin: isCollapsed ? '0' : '2px 0 0 0' }}>
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
          padding: isCollapsed ? '10px 6px' : '10px 14px',
          borderTop: '1px solid #161A22',
          background: '#06080D',
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
        }}
        title={isCollapsed ? `Health: ${healthStatus} • Region: ${activeWorkspace.region} (Click to expand)` : undefined}
        onClick={isCollapsed ? toggleCollapsed : undefined}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', color: '#94A3B8', cursor: isCollapsed ? 'pointer' : 'default' }}>
          <span
            style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: healthStatus === 'connected' ? '#10B981' : '#F59E0B',
              boxShadow: healthStatus === 'connected' ? '0 0 8px #10B981' : 'none',
              flexShrink: 0,
            }}
          />
          {!isCollapsed && <span style={{ fontWeight: 600 }}>{activeWorkspace.region}</span>}
        </div>
        {!isCollapsed && <span style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>v1.0 SaaS</span>}
      </div>
    </aside>
  );
};

export default Sidebar;
