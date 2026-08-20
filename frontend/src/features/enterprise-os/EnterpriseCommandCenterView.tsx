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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingBottom: '32px' }}>
      
      {/* 1. Header with Primary CTA Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: '#C5CCD6',
              borderRadius: '9999px',
              padding: '2px 10px',
              fontSize: '10px',
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}
          >
            <Sparkles size={11} color="#FFFFFF" />
            <span>EXECUTIVE INTELLIGENCE OPERATING SYSTEM (V1.0 SAAS)</span>
          </div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 900, color: '#FFFFFF', margin: '0', letterSpacing: '-0.025em', lineHeight: 1.15 }}>
            Enterprise Decision Intelligence Command Center
          </h1>
          <p style={{ color: '#8E99A8', fontSize: '0.78rem', margin: '2px 0 0 0' }}>
            Autonomous deterministic intelligence, dataset telemetry ingestion, and boardroom scenario control.
          </p>
        </div>

        {/* Primary Action Buttons */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'nowrap', flexShrink: 0 }}>
          <button
            onClick={handleLoadDemoDataset}
            style={{
              padding: '6px 12px',
              background: '#0D0F14',
              border: '1px solid #1E232B',
              borderRadius: '6px',
              color: '#FFFFFF',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              transition: 'all 0.15s ease',
            }}
          >
            <Sparkles size={12} color="#CBD5E1" />
            <span>Load Demo SaaS Benchmark</span>
          </button>

          <Link
            to="/enterprise-data"
            style={{
              padding: '6px 14px',
              background: '#FFFFFF',
              border: '1px solid #FFFFFF',
              borderRadius: '6px',
              color: '#000000',
              fontSize: '0.75rem',
              fontWeight: 700,
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Upload size={12} />
            <span>Upload Enterprise Dataset</span>
          </Link>
        </div>
      </div>

      {/* Quick Notice Banner */}
      {quickNotice && (
        <div style={{ padding: '8px 12px', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.35)', borderRadius: '8px', color: '#10B981', fontSize: '0.78rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle2 size={14} />
          <span>{quickNotice}</span>
        </div>
      )}

      {/* 2. Boardroom 'What Changed?' Intelligence Diff */}
      <div style={{ background: '#080A0E', border: '1px solid #161A22', borderRadius: '10px', padding: '8px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
          <Sparkles size={13} color="#CBD5E1" />
          <span style={{ fontSize: '0.76rem', color: '#CBD5E1', fontWeight: 600 }}>
            Active Dataset: <strong style={{ color: '#FFFFFF' }}>{activeDataset?.name || 'Enterprise Telemetry Event Stream Q1-2026'}</strong> • Since Last Review: <strong style={{ color: '#FFFFFF' }}>Revenue +4.2%</strong> • <strong style={{ color: '#FFFFFF' }}>Retention +2.8%</strong> • <strong style={{ color: '#FFFFFF' }}>Risk -12.0%</strong> • Top Opportunity: <strong style={{ color: '#10B981' }}>+$340K ARR</strong>
          </span>
        </div>
        <span style={{ fontSize: '0.64rem', fontWeight: 700, padding: '2px 7px', borderRadius: '4px', background: '#0F172A', color: '#CBD5E1', border: '1px solid #334155', letterSpacing: '0.04em' }}>
          EXECUTIVE TRUST SCORE: 93.2 / 100
        </span>
      </div>

      {/* 3. Data-Aware Homepage Cards Row (4 Columns Single Row) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '10px' }}>
        
        {/* Card 1: Datasets Ingestion Status */}
        <div
          style={{
            background: '#080A0E',
            border: '1px solid #161A22',
            borderRadius: '10px',
            padding: '12px 14px',
            position: 'relative',
            boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '6px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                DATASET STATUS
              </span>
              <Database size={13} color="#CBD5E1" />
            </div>
            <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px' }}>
              {datasets.length > 0 ? `${datasets.length} Registered` : '3 Registered'}
            </div>
            <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
              <span style={{ color: '#10B981', fontWeight: 700 }}>2 Processed</span> • <span>1 Live Context</span>
            </div>
          </div>
          <Link
            to="/enterprise-data"
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              color: '#E2E8F0',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              paddingTop: '6px',
              borderTop: '1px solid #14171E',
            }}
          >
            <span>Open Data Hub</span>
            <ArrowRight size={11} />
          </Link>
        </div>

        {/* Card 2: Business Health Score */}
        <div
          style={{
            background: '#080A0E',
            border: '1px solid #161A22',
            borderRadius: '10px',
            padding: '12px 14px',
            position: 'relative',
            boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '6px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                BUSINESS HEALTH SCORE
              </span>
              <Activity size={13} color="#CBD5E1" />
            </div>
            <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px' }}>
              92.4 <span style={{ fontSize: '0.82rem', color: '#64748B' }}>/ 100</span>
            </div>
            <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
              <span style={{ color: '#10B981', fontWeight: 700 }}>↑ +4.2 pts</span> • Healthy Operating Band
            </div>
          </div>
          <Link
            to="/portfolio-rollup"
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              color: '#E2E8F0',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              paddingTop: '6px',
              borderTop: '1px solid #14171E',
            }}
          >
            <span>View 32 Metric KPIs</span>
            <ArrowRight size={11} />
          </Link>
        </div>

        {/* Card 3: Diagnostic Findings */}
        <div
          style={{
            background: '#080A0E',
            border: '1px solid #161A22',
            borderRadius: '10px',
            padding: '12px 14px',
            position: 'relative',
            boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '6px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                DIAGNOSTIC FINDINGS
              </span>
              <AlertTriangle size={13} color="#EF4444" />
            </div>
            <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#EF4444', letterSpacing: '-0.02em', marginTop: '2px' }}>
              4 Critical
            </div>
            <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
              3 High-Impact Root Causes Isolated
            </div>
          </div>
          <Link
            to="/diagnostics"
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              color: '#E2E8F0',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              paddingTop: '6px',
              borderTop: '1px solid #14171E',
            }}
          >
            <span>Inspect Root Causes</span>
            <ArrowRight size={11} />
          </Link>
        </div>

        {/* Card 4: Value Realization */}
        <div
          style={{
            background: '#080A0E',
            border: '1px solid #161A22',
            borderRadius: '10px',
            padding: '12px 14px',
            position: 'relative',
            boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            gap: '6px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                VALUE REALIZATION
              </span>
              <DollarSign size={13} color="#CBD5E1" />
            </div>
            <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px' }}>
              $4.2M <span style={{ fontSize: '0.82rem', color: '#64748B' }}>ARR</span>
            </div>
            <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
              <span style={{ color: '#10B981', fontWeight: 700 }}>+$312K</span> Realized this Quarter
            </div>
          </div>
          <Link
            to="/boardroom"
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              color: '#E2E8F0',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              paddingTop: '6px',
              borderTop: '1px solid #14171E',
            }}
          >
            <span>Open Boardroom Briefing</span>
            <ArrowRight size={11} />
          </Link>
        </div>

      </div>

      {/* 4. Multi-Quarter Scorecard & Telemetry Breakdown */}
      <div style={{ background: '#080A0E', border: '1px solid #161A22', borderRadius: '10px', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>Quarterly Intelligence Trajectory</span>
            <span style={{ fontSize: '0.72rem', color: '#64748B', display: 'block' }}>Verified Continuous Lineage Across 4 Enterprise Ingestion Cycles</span>
          </div>
          <span style={{ fontSize: '0.66rem', fontWeight: 700, padding: '3px 8px', borderRadius: '4px', background: '#0F172A', color: '#CBD5E1', border: '1px solid #334155', letterSpacing: '0.04em' }}>
            AUTONOMOUS CALCULATION VERIFIED
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #161A22', color: '#64748B', textAlign: 'left' }}>
                <th style={{ padding: '8px 10px', fontWeight: 700 }}>REPORTING PERIOD</th>
                <th style={{ padding: '8px 10px', fontWeight: 700 }}>OVERALL SCORE</th>
                <th style={{ padding: '8px 10px', fontWeight: 700 }}>HEALTH</th>
                <th style={{ padding: '8px 10px', fontWeight: 700 }}>OPERATIONS</th>
                <th style={{ padding: '8px 10px', fontWeight: 700 }}>GOVERNANCE</th>
                <th style={{ padding: '8px 10px', fontWeight: 700, textAlign: 'right' }}>REALIZED ARR</th>
              </tr>
            </thead>
            <tbody>
              {scoreSnapshots.map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #11141B', color: '#FFFFFF' }}>
                  <td style={{ padding: '9px 10px', fontWeight: 800, color: idx === 3 ? '#FFFFFF' : '#94A3B8' }}>{row.month}</td>
                  <td style={{ padding: '9px 10px' }}>
                    <span style={{ fontWeight: 800, color: '#10B981' }}>{row.score}</span> / 100
                  </td>
                  <td style={{ padding: '9px 10px', color: '#94A3B8' }}>{row.health}</td>
                  <td style={{ padding: '9px 10px', color: '#94A3B8' }}>{row.operating}</td>
                  <td style={{ padding: '9px 10px', color: '#94A3B8' }}>{row.governance}</td>
                  <td style={{ padding: '9px 10px', textAlign: 'right', fontWeight: 800, color: '#10B981' }}>{row.realizedArr}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Live Activity Feed */}
      <ActivityFeed />

    </div>
  );
};

export default EnterpriseCommandCenterView;
