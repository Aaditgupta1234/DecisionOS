import React from 'react';
import { Globe, TrendingUp, AlertTriangle, ArrowRight, ShieldCheck, PieChart, Layers, GitMerge, Link2 } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';
import { Link } from 'react-router-dom';

export interface CrossPortfolioDependency {
  id: string;
  sourceUnit: string;
  sourceRegion: string;
  targetUnit: string;
  targetRegion: string;
  dependencyType: 'BLOCKS' | 'ACCELERATES' | 'REQUIRES_CAPITAL_FROM';
  impactDescription: string;
  status: 'BLOCKED' | 'ALIGNED' | 'RESOLVING';
}

export const PortfolioRollupView: React.FC = () => {
  const dependencies: CrossPortfolioDependency[] = [
    {
      id: 'dep-1',
      sourceUnit: 'APAC Regional Logistics Automation',
      sourceRegion: 'APAC',
      targetUnit: 'North America Enterprise SaaS Rollout',
      targetRegion: 'North America',
      dependencyType: 'BLOCKS',
      impactDescription: 'APAC transit latency (-$140K drag) delays enterprise multi-regional SLA guarantees.',
      status: 'BLOCKED',
    },
    {
      id: 'dep-2',
      sourceUnit: 'Cloud Infrastructure Migration',
      sourceRegion: 'North America',
      targetUnit: 'Europe Retail Fulfillment Scale',
      targetRegion: 'Europe',
      dependencyType: 'ACCELERATES',
      impactDescription: 'Unified data ingestion reduces European fulfillment sync latency by 45%.',
      status: 'ALIGNED',
    },
  ];

  const regions = [
    {
      name: 'North America Enterprise',
      arr: '$7.4M',
      growth: '+12.4%',
      health: '88.2',
      status: 'LEADER',
      primaryDivision: 'Retail Logistics & B2B SaaS',
      dragStatus: 'NONE',
    },
    {
      name: 'Europe & UK Operations',
      arr: '$3.8M',
      growth: '+8.1%',
      health: '84.1',
      status: 'HEALTHY',
      primaryDivision: 'Cross-Border Fulfillment',
      dragStatus: 'NONE',
    },
    {
      name: 'APAC Expansion Hub',
      arr: '$1.2M',
      growth: '-4.8%',
      health: '72.4',
      status: 'DRAGGING_GROWTH',
      primaryDivision: 'Last-Mile Freight Nodes',
      dragStatus: 'PRIMARY_ENTERPRISE_DRAG (-$140K ARR)',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Enterprise Scale Hierarchy & Drag Detection
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Multi-Portfolio Hierarchy & Enterprise Rollup
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/capital-allocation" style={{ textDecoration: 'none' }}>
            <Button variant="primary" size="sm">
              Open Capital Allocation Studio ($1M) →
            </Button>
          </Link>
        </div>
      </div>

      {/* Hero Metric Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL ENTERPRISE ARR" value="$12.4M" sublabel="Across 3 Global Operating Regions" valueColor="#10B981" />
        <MetricTile label="PORTFOLIO COMPOSITE HEALTH" value="85.0 / 100" sublabel="↑ +11.0 pts Since Q4 Rebalancing" valueColor="#38BDF8" />
        <MetricTile label="PRIMARY ENTERPRISE DRAG" value="APAC Logistics" sublabel="-$140K Dragging Regional ARR" valueColor="#EF4444" />
        <MetricTile label="CROSS-PORTFOLIO DEPENDENCIES" value="2 Blockers" sublabel="Cross-Regional Strategy Alignment" valueColor="#A855F7" />
      </div>

      {/* Automated Drag Warning Banner */}
      <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '12px', padding: '18px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertTriangle size={20} color="#EF4444" />
          <div>
            <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>
              Automated Drag Diagnostic: APAC Regional Logistics
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
              Carrier route transit latency is eroding customer retention (-6.8% vs median). Reallocating capital to automated sorting resolves -$140K drag.
            </div>
          </div>
        </div>
        <Link to="/diagnostics" style={{ textDecoration: 'none' }}>
          <Button variant="danger" size="sm">
            Investigate Root Causes →
          </Button>
        </Link>
      </div>

      {/* Cross-Portfolio Dependencies Intelligence */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>
            Cross-Portfolio Dependency Intelligence
          </span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Multi-Division Strategy Alignment</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {dependencies.map((d) => (
            <div
              key={d.id}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '10px',
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
                  <Link2 size={16} color={d.status === 'BLOCKED' ? '#EF4444' : '#10B981'} />
                  <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>
                    {d.sourceUnit} ({d.sourceRegion})
                  </span>
                  <Badge variant={d.dependencyType === 'BLOCKS' ? 'rose' : 'emerald'} size="sm">
                    {d.dependencyType}
                  </Badge>
                  <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>
                    {d.targetUnit} ({d.targetRegion})
                  </span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  {d.impactDescription}
                </div>
              </div>

              <Badge variant={d.status === 'BLOCKED' ? 'rose' : 'emerald'} size="sm">
                STATUS: {d.status}
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Regional Portfolios Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Global Regional Operating Portfolios</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Multi-Tenant Hierarchy</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {regions.map((r, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '10px',
                padding: '18px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Globe size={16} color="#38BDF8" />
                  <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{r.name}</span>
                  <Badge variant={r.status === 'DRAGGING_GROWTH' ? 'rose' : 'emerald'} size="sm">
                    {r.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  ARR: <strong style={{ color: '#FFFFFF' }}>{r.arr}</strong> ({r.growth}) • Health: <strong style={{ color: '#10B981' }}>{r.health}</strong> • Divisions: {r.primaryDivision}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {r.dragStatus !== 'NONE' && (
                  <span style={{ fontSize: '0.74rem', color: '#EF4444', fontWeight: 800 }}>
                    {r.dragStatus}
                  </span>
                )}
                <Link to="/portfolio" style={{ textDecoration: 'none' }}>
                  <Button variant="secondary" size="sm">
                    Open Scorecard →
                  </Button>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
