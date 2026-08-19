import React from 'react';
import { ShieldCheck, CheckCircle2, AlertCircle, ArrowLeft, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';

export const MonitoringCoverageView: React.FC = () => {
  const coverageStreams = [
    { name: 'Revenue & ARR Telemetry Streams', coverage: '100%', rules: '24 Rules', status: 'FULLY_MONITORED' },
    { name: 'Customer Retention & Cohort Churn', coverage: '100%', rules: '18 Rules', status: 'FULLY_MONITORED' },
    { name: 'Predictive Forecast Deviation Envelopes', coverage: '100%', rules: '32 Rules', status: 'FULLY_MONITORED' },
    { name: 'Strategic Initiatives & Milestone Delays', coverage: '92.0%', rules: '26 Rules', status: 'ACTIVE_MONITORING' },
    { name: 'Digital Twin Capacity Constraints', coverage: '95.0%', rules: '18 Rules', status: 'ACTIVE_MONITORING' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      <div>
        <Link
          to="/monitoring-center"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#64748B', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', marginBottom: '8px' }}
        >
          <ArrowLeft size={14} />
          <span>Back to Monitoring Command Center</span>
        </Link>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Enterprise Governance Audit
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Monitoring Coverage & Governance Audit
        </h1>
      </div>

      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>OVERALL COVERAGE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>96.4%</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>MONITORED KPIS</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>32 / 34 KPIs</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>ACTIVE RULES</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>118 Rules</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>UNMONITORED METRICS</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#94A3B8', marginTop: '2px' }}>2 Metrics</div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {coverageStreams.map((stream, idx) => (
          <div
            key={idx}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '12px',
              padding: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <CheckCircle2 size={18} color="#10B981" />
              <div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>{stream.name}</div>
                <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{stream.rules}</div>
              </div>
            </div>
            <span style={{ fontSize: '0.85rem', fontWeight: 900, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '4px 10px', borderRadius: '6px' }}>
              {stream.coverage}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
