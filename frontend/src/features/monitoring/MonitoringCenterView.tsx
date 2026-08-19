import React, { useState } from 'react';
import { Activity, AlertTriangle, ShieldCheck, TrendingDown, TrendingUp, CheckCircle, Clock, Filter, Eye } from 'lucide-react';
import { ExplainabilityDrawer } from '../../components/workspace/ExplainabilityDrawer';

export const MonitoringCenterView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'DRIFT' | 'ALERTS' | 'RISKS'>('DRIFT');
  const [alertFilter, setAlertFilter] = useState('ALL');
  const [isExplainOpen, setIsExplainOpen] = useState(false);
  const [explainTitle, setExplainTitle] = useState('Customer Retention Drift');
  const [explainValue, setExplainValue] = useState('79.5% (Actual) vs 85.8% (Target) — -7.3% Drift');

  const alerts = [
    { id: 'ALT-101', title: 'CRITICAL: Customer Retention Drift (-7.3%)', status: 'OPEN', severity: 'CRITICAL', corridor: 'Southeast Region', time: '12m ago' },
    { id: 'ALT-102', title: 'HIGH: Secondary Hub Carrier SLA Miss', status: 'ACKNOWLEDGED', severity: 'HIGH', corridor: 'Southeast Hub B', time: '1h ago' },
    { id: 'ALT-103', title: 'MEDIUM: Delivery Latency Exceeds 5.0d', status: 'IN_PROGRESS', severity: 'MEDIUM', corridor: 'Northern Corridors', time: '3h ago' },
    { id: 'ALT-104', title: 'RESOLVED: Payment Gateway Retry Outage', status: 'RESOLVED', severity: 'LOW', corridor: 'Payment Engine', time: '1d ago' },
  ];

  const filteredAlerts = alertFilter === 'ALL' ? alerts : alerts.filter((a) => a.status === alertFilter);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            Continuous Intelligence & Telemetry
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Continuous Monitoring Center
          </h1>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '6px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', padding: '4px', borderRadius: '8px' }}>
          {(['DRIFT', 'ALERTS', 'RISKS'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '6px 14px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === tab ? '#0284C7' : 'transparent',
                color: activeTab === tab ? '#FFFFFF' : '#94A3B8',
                fontSize: '0.8rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              {tab === 'DRIFT' ? 'KPI Drift Telemetry' : tab === 'ALERTS' ? 'Executive Alerts' : 'Risk Escalation'}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Drift Panel */}
      {activeTab === 'DRIFT' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            {/* Drift Card 1: Retention */}
            <div
              style={{ background: '#090D14', border: '1px solid #EF4444', borderRadius: '10px', padding: '20px', cursor: 'pointer' }}
              onClick={() => {
                setExplainTitle('Customer Retention Rate Drift');
                setExplainValue('79.5% (Actual) vs 85.8% (Target) — -7.3% Drift');
                setIsExplainOpen(true);
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.72rem', color: '#EF4444', fontWeight: 800, textTransform: 'uppercase' }}>HIGH DRIFT DETECTED</span>
                <AlertTriangle size={16} color="#EF4444" />
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>Customer Retention Rate</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginTop: '8px' }}>
                <span style={{ fontSize: '2rem', fontWeight: 900, color: '#EF4444' }}>79.5%</span>
                <span style={{ fontSize: '0.85rem', color: '#64748B' }}>Target: 85.8% (-7.3% variance)</span>
              </div>
              <div style={{ marginTop: '12px', fontSize: '0.75rem', color: '#38BDF8', fontWeight: 600 }}>
                Click to inspect root cause DAG & remedial recommendations →
              </div>
            </div>

            {/* Drift Card 2: Latency */}
            <div
              style={{ background: '#090D14', border: '1px solid #F59E0B', borderRadius: '10px', padding: '20px', cursor: 'pointer' }}
              onClick={() => {
                setExplainTitle('Delivery Latency Drift');
                setExplainValue('5.4 Days (Actual) vs 3.2 Days (Baseline) — +68.8% Delay');
                setIsExplainOpen(true);
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.72rem', color: '#F59E0B', fontWeight: 800, textTransform: 'uppercase' }}>MODERATE DRIFT</span>
                <AlertTriangle size={16} color="#F59E0B" />
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>Delivery Latency (Days)</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginTop: '8px' }}>
                <span style={{ fontSize: '2rem', fontWeight: 900, color: '#F59E0B' }}>5.4d</span>
                <span style={{ fontSize: '0.85rem', color: '#64748B' }}>Baseline: 3.2d (+68.8% delay)</span>
              </div>
              <div style={{ marginTop: '12px', fontSize: '0.75rem', color: '#38BDF8', fontWeight: 600 }}>
                Click to inspect secondary hub dispatch bottleneck →
              </div>
            </div>

            {/* Drift Card 3: SLA Compliance */}
            <div
              style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '10px', padding: '20px', cursor: 'pointer' }}
              onClick={() => {
                setExplainTitle('Courier SLA Compliance');
                setExplainValue('78.4% (Actual) vs 92.0% (Target) — -13.6% Drift');
                setIsExplainOpen(true);
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.72rem', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase' }}>ACTIVE MONITORING</span>
                <Activity size={16} color="#38BDF8" />
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>Courier SLA Compliance</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginTop: '8px' }}>
                <span style={{ fontSize: '2rem', fontWeight: 900, color: '#38BDF8' }}>78.4%</span>
                <span style={{ fontSize: '0.85rem', color: '#64748B' }}>Target: 92.0% (-13.6% variance)</span>
              </div>
              <div style={{ marginTop: '12px', fontSize: '0.75rem', color: '#38BDF8', fontWeight: 600 }}>
                Click to view automated penalty trigger →
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Alerts Center Tab */}
      {activeTab === 'ALERTS' && (
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>Executive Alert Queue (5-State Workflow)</div>
            <div style={{ display: 'flex', gap: '6px' }}>
              {['ALL', 'OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED'].map((f) => (
                <button
                  key={f}
                  onClick={() => setAlertFilter(f)}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '4px',
                    border: '1px solid #1E293B',
                    background: alertFilter === f ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
                    color: alertFilter === f ? '#38BDF8' : '#94A3B8',
                    fontSize: '0.74rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredAlerts.map((a) => (
              <div
                key={a.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                    <span style={{ fontSize: '0.68rem', fontWeight: 800, color: a.severity === 'CRITICAL' ? '#EF4444' : a.severity === 'HIGH' ? '#F59E0B' : '#38BDF8' }}>
                      {a.severity}
                    </span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{a.title}</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Corridor: {a.corridor} • {a.time}</div>
                </div>
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 800,
                    padding: '3px 8px',
                    borderRadius: '12px',
                    background: a.status === 'OPEN' ? 'rgba(239, 68, 68, 0.15)' : a.status === 'RESOLVED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                    color: a.status === 'OPEN' ? '#EF4444' : a.status === 'RESOLVED' ? '#10B981' : '#38BDF8',
                  }}
                >
                  {a.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Escalation Panel */}
      {activeTab === 'RISKS' && (
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Systemic Risk Escalation Matrix</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '16px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700 }}>SYSTEMIC RISK INDEX</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#F59E0B', marginTop: '4px' }}>14.1 / 100</div>
              <div style={{ fontSize: '0.75rem', color: '#10B981', marginTop: '4px' }}>-10.2 pts reduction vs prior cycle</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '16px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700 }}>RISK VELOCITY</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#10B981', marginTop: '4px' }}>STABLE</div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>Velocity vector: +0.02 / week</div>
            </div>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '16px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700 }}>UNMITIGATED BOTTLENECKS</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 900, color: '#38BDF8', marginTop: '4px' }}>0 CRITICAL</div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', marginTop: '4px' }}>2 High, 5 Moderate</div>
            </div>
          </div>
        </div>
      )}

      {/* Explainability Drawer */}
      <ExplainabilityDrawer
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title={explainTitle}
        metricValue={explainValue}
      />
    </div>
  );
};
