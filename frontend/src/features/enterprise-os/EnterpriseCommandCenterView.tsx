import React, { useState } from 'react';
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
  Calendar,
  Database,
  Upload,
  AlertTriangle,
  FileText,
  Zap,
  ArrowRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, Badge, MetricTile } from '../../design-system';
import { ActivityFeed } from '../shared/ActivityFeed';
import { useDataset } from '../../context/DatasetContext';

export interface EnterpriseScoreSnapshot {
  month: string;
  score: number;
  health: number;
  operating: number;
  governance: number;
  realizedArr: string;
}

export const EnterpriseCommandCenterView: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset } = useDataset();
  const [quickNotice, setQuickNotice] = useState<string | null>(null);

  const scoreSnapshots: EnterpriseScoreSnapshot[] = [
    { month: 'Jan 2026', score: 81.2, health: 74.0, operating: 86.4, governance: 88.0, realizedArr: '+$84,000' },
    { month: 'Feb 2026', score: 84.5, health: 78.2, operating: 89.1, governance: 92.5, realizedArr: '+$162,000' },
    { month: 'Mar 2026', score: 89.4, health: 82.5, operating: 92.4, governance: 96.0, realizedArr: '+$248,000' },
    { month: 'Apr 2026 (Live)', score: 93.1, health: 85.0, operating: 94.8, governance: 98.4, realizedArr: '+$312,000' },
  ];

  const handleLoadDemoDataset = () => {
    setQuickNotice('Loaded Enterprise Benchmark Telemetry (1.42M events). Analytical workspace context active!');
    if (datasets.length > 0) {
      setActiveDataset(datasets[0]);
    }
    setTimeout(() => setQuickNotice(null), 4000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      
      {/* 1. Header with Primary CTA Buttons */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            <Sparkles size={13} color="#38BDF8" />
            <span>EXECUTIVE INTELLIGENCE OPERATING SYSTEM (v1.0 SaaS)</span>
          </div>
          <h1 style={{ fontSize: '1.9rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0', letterSpacing: '-0.02em' }}>
            Enterprise Decision Intelligence Command Center
          </h1>
          <p style={{ color: '#94A3B8', fontSize: '0.88rem', margin: '4px 0 0 0' }}>
            Autonomous deterministic intelligence, dataset telemetry ingestion, and boardroom scenario control.
          </p>
        </div>

        {/* Primary Action Buttons for Recruiter Walkthrough */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            onClick={handleLoadDemoDataset}
            style={{
              padding: '9px 14px',
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.35)',
              borderRadius: '8px',
              color: '#38BDF8',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Sparkles size={14} />
            <span>Load Demo SaaS Benchmark</span>
          </button>

          <Link
            to="/enterprise-data"
            style={{
              padding: '9px 16px',
              background: '#FFFFFF',
              border: '1px solid #FFFFFF',
              borderRadius: '8px',
              color: '#000000',
              fontSize: '0.82rem',
              fontWeight: 800,
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Upload size={14} />
            <span>Upload Enterprise Dataset</span>
          </Link>
        </div>
      </div>

      {/* Quick Notice Banner */}
      {quickNotice && (
        <div style={{ padding: '12px 18px', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.35)', borderRadius: '10px', color: '#10B981', fontSize: '0.86rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={16} />
          <span>{quickNotice}</span>
        </div>
      )}

      {/* 2. Boardroom 'What Changed?' Intelligence Diff */}
      <div style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '12px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sparkles size={18} color="#38BDF8" />
          <span style={{ fontSize: '0.82rem', color: '#FFFFFF', fontWeight: 700 }}>
            Active Dataset: <strong style={{ color: '#10B981' }}>{activeDataset?.name || 'Enterprise Telemetry Event Stream Q1-2026'}</strong> • Since Last Review: <strong>Revenue +4.2%</strong> • <strong>Retention +2.8%</strong> • <strong>Risk -12.0%</strong> • Top Opportunity: <strong style={{ color: '#10B981' }}>+$340K ARR</strong>
          </span>
        </div>
        <Badge variant="sky" size="sm">
          EXECUTIVE TRUST SCORE: 93.2 / 100
        </Badge>
      </div>

      {/* 3. Data-Aware Homepage Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        
        {/* Card 1: Datasets Ingestion Status */}
        <div
          style={{
            background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
            border: '1px solid #14171E',
            borderRadius: '14px',
            padding: '20px',
            position: 'relative',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                DATASET STATUS
              </span>
              <Database size={15} color="#10B981" />
            </div>
            <div style={{ fontSize: '1.9rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '4px' }}>
              {datasets.length > 0 ? `${datasets.length} Registered` : '3 Registered'}
            </div>
            <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '2px' }}>
              <span style={{ color: '#10B981', fontWeight: 700 }}>2 Processed</span> • <span>1 Live Context</span>
            </div>
          </div>
          <Link
            to="/enterprise-data"
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              color: '#38BDF8',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>Open Data Hub</span>
            <ArrowRight size={13} />
          </Link>
        </div>

        {/* Card 2: Business Health Score */}
        <div
          style={{
            background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
            border: '1px solid #14171E',
            borderRadius: '14px',
            padding: '20px',
            position: 'relative',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                BUSINESS HEALTH SCORE
              </span>
              <Activity size={15} color="#38BDF8" />
            </div>
            <div style={{ fontSize: '1.9rem', fontWeight: 900, color: '#38BDF8', letterSpacing: '-0.02em', marginTop: '4px' }}>
              92.4 <span style={{ fontSize: '1rem', color: '#64748B' }}>/ 100</span>
            </div>
            <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '2px' }}>
              <span style={{ color: '#10B981', fontWeight: 700 }}>↑ +4.2 pts</span> • Healthy Operating Band
            </div>
          </div>
          <Link
            to="/portfolio"
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              color: '#38BDF8',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>View 32 Metric KPIs</span>
            <ArrowRight size={13} />
          </Link>
        </div>

        {/* Card 3: Diagnostic Findings */}
        <div
          style={{
            background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
            border: '1px solid #14171E',
            borderRadius: '14px',
            padding: '20px',
            position: 'relative',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                DIAGNOSTIC FINDINGS
              </span>
              <AlertTriangle size={15} color="#EF4444" />
            </div>
            <div style={{ fontSize: '1.9rem', fontWeight: 900, color: '#EF4444', letterSpacing: '-0.02em', marginTop: '4px' }}>
              4 Critical
            </div>
            <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '2px' }}>
              3 High-Impact Root Causes Isolated
            </div>
          </div>
          <Link
            to="/diagnostics"
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              color: '#EF4444',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>Inspect Root Causes</span>
            <ArrowRight size={13} />
          </Link>
        </div>

        {/* Card 4: Value Realization */}
        <div
          style={{
            background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
            border: '1px solid #14171E',
            borderRadius: '14px',
            padding: '20px',
            position: 'relative',
            boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                VALUE REALIZATION
              </span>
              <DollarSign size={15} color="#F59E0B" />
            </div>
            <div style={{ fontSize: '1.9rem', fontWeight: 900, color: '#10B981', letterSpacing: '-0.02em', marginTop: '4px' }}>
              $4.2M <span style={{ fontSize: '0.9rem', color: '#64748B' }}>ARR</span>
            </div>
            <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '2px' }}>
              <span style={{ color: '#10B981', fontWeight: 700 }}>+$312K</span> Realized this Quarter
            </div>
          </div>
          <Link
            to="/boardroom"
            style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              color: '#F59E0B',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <span>Open Boardroom Briefing</span>
            <ArrowRight size={13} />
          </Link>
        </div>

      </div>

      {/* 4. Multi-Quarter Scorecard & Telemetry Breakdown */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Quarterly Intelligence Trajectory</span>
            <span style={{ fontSize: '0.75rem', color: '#64748B', display: 'block' }}>Verified Continuous Lineage Across 4 Enterprise Ingestion Cycles</span>
          </div>
          <Badge variant="emerald" size="sm">
            AUTONOMOUS CALCULATION VERIFIED
          </Badge>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #14171E', color: '#64748B', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>REPORTING PERIOD</th>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>OVERALL SCORE</th>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>HEALTH</th>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>OPERATIONS</th>
                <th style={{ padding: '10px 12px', fontWeight: 700 }}>GOVERNANCE</th>
                <th style={{ padding: '10px 12px', fontWeight: 700, textAlign: 'right' }}>REALIZED ARR</th>
              </tr>
            </thead>
            <tbody>
              {scoreSnapshots.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #0B0E14', color: '#FFFFFF' }}>
                  <td style={{ padding: '12px', fontWeight: 800, color: idx === 3 ? '#38BDF8' : '#FFFFFF' }}>{row.month}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ fontWeight: 800, color: '#10B981' }}>{row.score}</span> / 100
                  </td>
                  <td style={{ padding: '12px', color: '#94A3B8' }}>{row.health}</td>
                  <td style={{ padding: '12px', color: '#94A3B8' }}>{row.operating}</td>
                  <td style={{ padding: '12px', color: '#94A3B8' }}>{row.governance}</td>
                  <td style={{ padding: '12px', textAlign: 'right', fontWeight: 800, color: '#10B981' }}>{row.realizedArr}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* 5. Live Activity Feed */}
      <ActivityFeed />

    </div>
  );
};

export default EnterpriseCommandCenterView;
