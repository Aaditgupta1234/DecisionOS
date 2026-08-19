import React, { useState } from 'react';
import {
  Activity,
  AlertTriangle,
  Clock,
  ShieldCheck,
  CheckCircle2,
  TrendingDown,
  Sparkles,
  ArrowUpRight,
  GitMerge,
  BarChart3,
  Award,
  Layers,
  BookOpen,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { AlertExplanationModal } from './AlertExplanationModal';
import { AlertLineageModal } from './AlertLineageModal';
import { AlertPostmortemModal } from './AlertPostmortemModal';

export const MonitoringCommandCenterView: React.FC = () => {
  const [selectedAlertCode, setSelectedAlertCode] = useState<string>('ALT-2026-089');
  const [showExplanation, setShowExplanation] = useState(false);
  const [showLineage, setShowLineage] = useState(false);
  const [showPostmortem, setShowPostmortem] = useState(false);

  const openAlerts = [
    {
      code: 'ALT-2026-089',
      title: 'Customer Retention Drift in Southeastern Corridor',
      severity: 'CRITICAL',
      team: 'Supply Chain & Logistics',
      owner: 'VP Operations',
      slaDue: '12 min left',
      projectedArrLoss: '-$82,000 ARR',
      priorityScore: 94.5,
      status: 'OPEN',
    },
    {
      code: 'ALT-2026-090',
      title: 'Secondary Hub Courier Latency SLA Breach',
      severity: 'HIGH',
      team: 'Supply Chain & Logistics',
      owner: 'Logistics Director',
      slaDue: '42 min left',
      projectedArrLoss: '-$45,000 ARR',
      priorityScore: 86.2,
      status: 'ACKNOWLEDGED',
    },
    {
      code: 'ALT-2026-091',
      title: 'Q1 Forecast Model Variance Envelope Expansion',
      severity: 'MEDIUM',
      team: 'Analytics & AI',
      owner: 'Lead Data Scientist',
      slaDue: 'Resolved',
      projectedArrLoss: '-$15,000 ARR',
      priorityScore: 68.0,
      status: 'RESOLVED',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#EF4444', fontWeight: 800 }}>
            Continuous Telemetry & Event Intelligence
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Autonomous Monitoring & Incident Command Center
          </h1>
        </div>

        {/* Quick Navigation Tabs */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <Link
            to="/monitoring/coverage"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#10B981', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <ShieldCheck size={14} />
            <span>Coverage (96.4%)</span>
          </Link>
          <Link
            to="/monitoring/analytics"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#38BDF8', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <BarChart3 size={14} />
            <span>Alert Analytics</span>
          </Link>
          <Link
            to="/monitoring/radar"
            style={{ padding: '8px 14px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', color: '#F59E0B', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Sparkles size={14} />
            <span>Predictive Risk Radar</span>
          </Link>
        </div>
      </div>

      {/* 4 Flagship Hero Metric Widgets */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {/* Widget 1: Open Critical Alerts */}
        <div style={{ background: '#090D14', border: '1px solid #EF4444', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#EF4444', fontWeight: 800, textTransform: 'uppercase' }}>OPEN CRITICAL ALERTS</span>
            <AlertTriangle size={18} color="#EF4444" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#FFFFFF' }}>1 Active</div>
          <div style={{ fontSize: '0.75rem', color: '#EF4444', fontWeight: 700 }}>
            Response SLA: 12m Remaining
          </div>
        </div>

        {/* Widget 2: Monitoring Health */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>TELEMETRY COVERAGE</span>
            <ShieldCheck size={18} color="#10B981" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>96.4%</div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700 }}>
            32 KPIs • 118 Active Rules
          </div>
        </div>

        {/* Widget 3: Prevented ARR Loss */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>PREVENTED ARR LOSS</span>
            <CheckCircle2 size={18} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8' }}>+$126,000</div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700 }}>
            83.5% Alert Effectiveness
          </div>
        </div>

        {/* Widget 4: Monitoring Maturity */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>MONITORING MATURITY</span>
            <Award size={18} color="#A855F7" />
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>91.8</div>
          <div style={{ fontSize: '0.75rem', color: '#A855F7', fontWeight: 800 }}>
            Grade A Enterprise Rating
          </div>
        </div>
      </div>

      {/* Incident Queue */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>Real-Time Alert & Incident Queue</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Continuously Evaluated</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {openAlerts.map((alert) => (
            <div
              key={alert.code}
              style={{
                padding: '20px',
                borderBottom: '1px solid #1E293B',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span
                  style={{
                    fontSize: '0.7rem',
                    fontWeight: 800,
                    padding: '3px 8px',
                    borderRadius: '4px',
                    background: alert.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                    color: alert.severity === 'CRITICAL' ? '#EF4444' : '#38BDF8',
                  }}
                >
                  {alert.severity}
                </span>

                <div>
                  <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#FFFFFF' }}>
                    {alert.code}: {alert.title}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '2px' }}>
                    Owner: {alert.owner} • Team: {alert.team} • SLA: <strong style={{ color: '#F59E0B' }}>{alert.slaDue}</strong>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#EF4444', marginRight: '8px' }}>
                  {alert.projectedArrLoss}
                </span>

                <button
                  onClick={() => {
                    setSelectedAlertCode(alert.code);
                    setShowExplanation(true);
                  }}
                  style={{
                    padding: '6px 10px',
                    background: 'rgba(56, 189, 248, 0.1)',
                    border: '1px solid rgba(56, 189, 248, 0.3)',
                    borderRadius: '6px',
                    color: '#38BDF8',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <Sparkles size={12} />
                  <span>Explain</span>
                </button>

                <button
                  onClick={() => {
                    setSelectedAlertCode(alert.code);
                    setShowLineage(true);
                  }}
                  style={{
                    padding: '6px 10px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    borderRadius: '6px',
                    color: '#10B981',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <GitMerge size={12} />
                  <span>Lineage</span>
                </button>

                <button
                  onClick={() => {
                    setSelectedAlertCode(alert.code);
                    setShowPostmortem(true);
                  }}
                  style={{
                    padding: '6px 10px',
                    background: 'rgba(168, 85, 247, 0.1)',
                    border: '1px solid rgba(168, 85, 247, 0.3)',
                    borderRadius: '6px',
                    color: '#A855F7',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <BookOpen size={12} />
                  <span>Postmortem</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modals */}
      <AlertExplanationModal
        isOpen={showExplanation}
        onClose={() => setShowExplanation(false)}
        alertCode={selectedAlertCode}
      />
      <AlertLineageModal
        isOpen={showLineage}
        onClose={() => setShowLineage(false)}
        alertCode={selectedAlertCode}
      />
      <AlertPostmortemModal
        isOpen={showPostmortem}
        onClose={() => setShowPostmortem(false)}
        alertCode={selectedAlertCode}
      />
    </div>
  );
};
