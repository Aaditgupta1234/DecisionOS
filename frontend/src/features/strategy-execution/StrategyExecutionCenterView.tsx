import React, { useState } from 'react';
import {
  Target,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  Layers,
  Sparkles,
  GitMerge,
  BarChart3,
  Award,
  Users,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const StrategyExecutionCenterView: React.FC = () => {
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

  const initiatives = [
    {
      code: 'INIT-2026-001',
      title: 'Secondary Hub Courier Rebalancing & Automated SLA Penalties',
      owner: 'VP Operations',
      sponsor: 'Chief Operating Officer',
      status: 'IN_PROGRESS',
      priority: 'CRITICAL',
      completion: 78,
      expectedArr: '+$124,000',
      actualArr: '+$118,000',
      realization: '95.2%',
      healthImpact: '+10.5 pts',
      riskReduction: '-9.8 pts',
      riskTier: 'GREEN',
    },
    {
      code: 'INIT-2026-002',
      title: 'Customer Win-Back Discount Credit Automation',
      owner: 'Director CX',
      sponsor: 'Chief Marketing Officer',
      status: 'IN_PROGRESS',
      priority: 'HIGH',
      completion: 52,
      expectedArr: '+$82,000',
      actualArr: '+$42,000',
      realization: '51.2%',
      healthImpact: '+4.0 pts',
      riskReduction: '-4.5 pts',
      riskTier: 'YELLOW',
    },
    {
      code: 'INIT-2026-003',
      title: 'Northern Corridor Fulfillment Node Expansion',
      owner: 'Supply Chain Lead',
      sponsor: 'Chief Operating Officer',
      status: 'PLANNED',
      priority: 'MEDIUM',
      completion: 0,
      expectedArr: '+$134,000',
      actualArr: '$0',
      realization: '0.0%',
      healthImpact: '+8.0 pts',
      riskReduction: '-5.0 pts',
      riskTier: 'GREEN',
    },
    {
      code: 'INIT-2026-004',
      title: 'Automated Tier-1 Logistics Route Consolidation',
      owner: 'Logistics Director',
      sponsor: 'Chief Financial Officer',
      status: 'COMPLETED',
      priority: 'HIGH',
      completion: 100,
      expectedArr: '+$72,000',
      actualArr: '+$68,500',
      realization: '95.1%',
      healthImpact: '+5.0 pts',
      riskReduction: '-8.1 pts',
      riskTier: 'GREEN',
    },
    {
      code: 'INIT-2026-005',
      title: 'Midwest Regional Transit Speed Modernization',
      owner: 'Operations Lead',
      sponsor: 'Chief Executive Officer',
      status: 'BLOCKED',
      priority: 'CRITICAL',
      completion: 24,
      expectedArr: '+$95,000',
      actualArr: '$12,000',
      realization: '12.6%',
      healthImpact: '+1.5 pts',
      riskReduction: '-1.0 pts',
      riskTier: 'RED',
    },
  ];

  const filtered = filterStatus === 'ALL'
    ? initiatives
    : initiatives.filter((i) => i.status === filterStatus);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Closed-Loop Enterprise Strategy Realization
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Strategy Execution & Benefits Realization Command Center
          </h1>
        </div>

        {/* Quick Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <Link
            to="/strategy-execution/dependencies"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#38BDF8', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <GitMerge size={14} />
            <span>Dependency DAG</span>
          </Link>
          <Link
            to="/strategy-execution/benefits"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#10B981', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <BarChart3 size={14} />
            <span>Benefits Realization</span>
          </Link>
          <Link
            to="/strategy-execution/calibration"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#F59E0B', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Sparkles size={14} />
            <span>Forecast Calibration</span>
          </Link>
          <Link
            to="/strategy-execution/performance"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#A855F7', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Award size={14} />
            <span>Executive Scorecards</span>
          </Link>
        </div>
      </div>

      {/* 4 Flagship Hero Metric Widgets */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
        {/* Widget 1: Initiative Portfolio */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>INITIATIVE PORTFOLIO</span>
            <Target size={18} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#FFFFFF' }}>42 Initiatives</div>
          <div style={{ display: 'flex', gap: '12px', fontSize: '0.78rem', marginTop: '4px' }}>
            <span style={{ color: '#38BDF8', fontWeight: 700 }}>28 Active</span>
            <span style={{ color: '#10B981', fontWeight: 700 }}>10 Completed</span>
            <span style={{ color: '#EF4444', fontWeight: 700 }}>4 At Risk</span>
          </div>
        </div>

        {/* Widget 2: Value Realization */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>VALUE REALIZATION</span>
            <TrendingUp size={18} color="#10B981" />
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <span style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>+$2.5M</span>
            <span style={{ fontSize: '0.85rem', color: '#64748B' }}>/ +$2.8M Target</span>
          </div>
          <div style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 800 }}>
            89.3% Realization Rate across Portfolio
          </div>
        </div>

        {/* Widget 3: Forecast Accuracy */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>FORECAST ACCURACY</span>
            <Sparkles size={18} color="#F59E0B" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B' }}>95.2%</div>
          <div style={{ fontSize: '0.78rem', color: '#94A3B8', fontWeight: 700 }}>
            ±4.8% Variance Envelope (42 Validated Cycles)
          </div>
        </div>

        {/* Widget 4: Execution Velocity */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>EXECUTION VELOCITY</span>
            <ShieldCheck size={18} color="#A855F7" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>76.4%</div>
          <div style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700 }}>
            +8.4% Milestone Completion MoM
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {['ALL', 'IN_PROGRESS', 'COMPLETED', 'BLOCKED', 'PLANNED'].map((st) => (
          <button
            key={st}
            onClick={() => setFilterStatus(st)}
            style={{
              padding: '6px 14px',
              borderRadius: '8px',
              border: 'none',
              background: filterStatus === st ? '#0284C7' : 'rgba(15, 23, 42, 0.8)',
              color: '#FFFFFF',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Strategic Initiatives Table */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>Strategic Initiatives Execution Roster</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Showing {filtered.length} Initiatives</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ background: 'rgba(15, 23, 42, 0.6)', color: '#64748B', borderBottom: '1px solid #1E293B' }}>
                <th style={{ padding: '12px 16px' }}>CODE</th>
                <th style={{ padding: '12px 16px' }}>INITIATIVE & SPONSOR</th>
                <th style={{ padding: '12px 16px' }}>STATUS</th>
                <th style={{ padding: '12px 16px' }}>PROGRESS</th>
                <th style={{ padding: '12px 16px' }}>EXPECTED ARR</th>
                <th style={{ padding: '12px 16px' }}>REALIZED ARR</th>
                <th style={{ padding: '12px 16px' }}>REALIZATION</th>
                <th style={{ padding: '12px 16px' }}>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.code} style={{ borderBottom: '1px solid #1E293B' }}>
                  <td style={{ padding: '14px 16px', fontWeight: 800, color: '#38BDF8' }}>{item.code}</td>
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ fontWeight: 800, color: '#FFFFFF', marginBottom: '2px' }}>{item.title}</div>
                    <div style={{ fontSize: '0.72rem', color: '#64748B' }}>Sponsor: {item.sponsor} • Owner: {item.owner}</div>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 800,
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background:
                          item.status === 'COMPLETED'
                            ? 'rgba(16, 185, 129, 0.15)'
                            : item.status === 'BLOCKED'
                            ? 'rgba(239, 68, 68, 0.15)'
                            : 'rgba(56, 189, 248, 0.15)',
                        color:
                          item.status === 'COMPLETED'
                            ? '#10B981'
                            : item.status === 'BLOCKED'
                            ? '#EF4444'
                            : '#38BDF8',
                      }}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ flex: 1, background: '#1E293B', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${item.completion}%`, background: item.completion === 100 ? '#10B981' : '#38BDF8', height: '100%' }} />
                      </div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8' }}>{item.completion}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 16px', fontWeight: 700, color: '#94A3B8' }}>{item.expectedArr}</td>
                  <td style={{ padding: '14px 16px', fontWeight: 800, color: '#10B981' }}>{item.actualArr}</td>
                  <td style={{ padding: '14px 16px', fontWeight: 800, color: item.realization === '95.2%' ? '#10B981' : '#F59E0B' }}>
                    {item.realization}
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <Link
                      to={`/strategy-execution/${item.code}`}
                      style={{
                        padding: '4px 10px',
                        background: 'rgba(15, 23, 42, 0.8)',
                        border: '1px solid #1E293B',
                        borderRadius: '6px',
                        color: '#38BDF8',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        textDecoration: 'none',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <span>Deep Dive</span>
                      <ArrowUpRight size={12} />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
