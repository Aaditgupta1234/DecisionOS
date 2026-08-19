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
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const EnterpriseCommandCenterView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            Executive Intelligence Operating System (v1.0)
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Decision Intelligence Command Center
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <Link
            to="/governance"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#10B981', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Scale size={14} />
            <span>Governance Registry</span>
          </Link>
          <Link
            to="/competitive-intelligence"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#F59E0B', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <TrendingUp size={14} />
            <span>Competitive Benchmarks</span>
          </Link>
          <Link
            to="/operating-system"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#A855F7', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Play size={14} />
            <span>Autonomous Playbooks</span>
          </Link>
        </div>
      </div>

      {/* 4 Flagship Hero Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>OPERATING SCORE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>94.8</div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700 }}>Grade A+ Enterprise Platform</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>REALIZED VALUE (ARR)</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8' }}>+$312,000</div>
          <div style={{ fontSize: '0.75rem', color: '#38BDF8', fontWeight: 700 }}>91.8% Decision Accuracy</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>COMPETITIVE POSITION</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B' }}>#4 of 28</div>
          <div style={{ fontSize: '0.75rem', color: '#F59E0B', fontWeight: 700 }}>85.7th Industry Percentile</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>ACTIVE PLAYBOOKS</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>4 Active</div>
          <div style={{ fontSize: '0.75rem', color: '#A855F7', fontWeight: 700 }}>Autonomous Cross-System Workflows</div>
        </div>
      </div>

      {/* Quick Overview Section */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Closed-Loop Enterprise OS Intelligence</span>
        <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5 }}>
          DecisionOS continuously aligns telemetry signals with competitive benchmarks, simulates Digital Twin scenarios, enforces governance policies, executes strategic initiatives, and attributes realized revenue gains back to executive decisions with <strong>91.8% Decision Accuracy</strong>.
        </div>
      </div>
    </div>
  );
};
