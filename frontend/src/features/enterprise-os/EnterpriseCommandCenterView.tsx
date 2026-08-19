import React from 'react';
import {
  Activity,
  Award,
  ShieldCheck,
  TrendingUp,
  Sparkles,
  Play,
  Layers,
  ArrowUpRight,
  BarChart3,
  Scale,
  CheckCircle2,
  DollarSign,
  Globe,
  Bot,
  BookOpen,
  ShieldAlert,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, Badge, MetricTile } from '../../design-system';
import { ActivityFeed } from '../shared/ActivityFeed';

export const EnterpriseCommandCenterView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            Executive Intelligence Operating System (v1.0 SaaS)
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Decision Intelligence Command Center
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <Link
            to="/portfolio-rollup"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#10B981', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Globe size={14} />
            <span>Multi-Portfolio Rollup</span>
          </Link>
          <Link
            to="/capital-allocation"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#A855F7', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <DollarSign size={14} />
            <span>Capital Allocation ($1M)</span>
          </Link>
          <Link
            to="/agents"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#38BDF8', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Bot size={14} />
            <span>Autonomous Agents</span>
          </Link>
        </div>
      </div>

      {/* Boardroom 'What Changed?' Intelligence Diff */}
      <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '12px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sparkles size={18} color="#38BDF8" />
          <span style={{ fontSize: '0.82rem', color: '#FFFFFF', fontWeight: 700 }}>
            Since Last Review: <strong>Revenue +4.2%</strong> • <strong>Retention +2.8%</strong> • <strong>Risk -12.0%</strong> • <strong>Accuracy +1.4%</strong> • Top New Opportunity: <strong style={{ color: '#10B981' }}>+$340K ARR</strong>
          </span>
        </div>
        <Badge variant="sky" size="sm">
          EXECUTIVE TRUST SCORE: 93.2 / 100
        </Badge>
      </div>

      {/* 4 Flagship Hero Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile
          label="ENTERPRISE INTELLIGENCE SCORE"
          value="93.1"
          sublabel="Composite of Health, OS & Governance"
          valueColor="#10B981"
        />
        <MetricTile
          label="REALIZED VALUE (ARR)"
          value="+$312,000"
          sublabel="91.8% Decision Accuracy Attribution"
          valueColor="#38BDF8"
        />
        <MetricTile
          label="COMPETITIVE POSITION"
          value="#4 of 28"
          sublabel="85.7th Industry Benchmark Percentile"
          valueColor="#F59E0B"
        />
        <MetricTile
          label="AUTONOMOUS AGENTS"
          value="6 Online"
          sublabel="Zero Ungrounded Generative Output"
          valueColor="#A855F7"
        />
      </div>

      {/* Grid: Closed Loop Overview & Platform Activity Feed */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Left: Intelligence Summary */}
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Closed-Loop Enterprise OS Intelligence</span>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.6 }}>
            DecisionOS continuously aligns telemetry signals with competitive benchmarks, simulates Digital Twin scenarios, enforces governance policies, executes strategic initiatives, and attributes realized revenue gains back to executive decisions with <strong>91.8% Decision Accuracy</strong>.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginTop: '8px' }}>
            <Link to="/governance" style={{ textDecoration: 'none' }}>
              <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', color: '#FFFFFF', fontSize: '0.78rem', fontWeight: 700 }}>
                ⚖️ Decision Governance →
              </div>
            </Link>
            <Link to="/competitive-intelligence" style={{ textDecoration: 'none' }}>
              <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', color: '#FFFFFF', fontSize: '0.78rem', fontWeight: 700 }}>
                📈 Benchmarks (98%) →
              </div>
            </Link>
            <Link to="/kpi-dictionary" style={{ textDecoration: 'none' }}>
              <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', color: '#FFFFFF', fontSize: '0.78rem', fontWeight: 700 }}>
                📖 KPI Dictionary →
              </div>
            </Link>
            <Link to="/risk-concentration" style={{ textDecoration: 'none' }}>
              <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', color: '#FFFFFF', fontSize: '0.78rem', fontWeight: 700 }}>
                ⚠️ Risk Concentration →
              </div>
            </Link>
          </div>
        </Card>

        {/* Right: Live Platform Activity Feed */}
        <ActivityFeed />
      </div>
    </div>
  );
};
