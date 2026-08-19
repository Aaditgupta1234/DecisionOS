import React from 'react';
import { BarChart3, Clock, ShieldCheck, TrendingUp, ArrowLeft, Award, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const AlertAnalyticsView: React.FC = () => {
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
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
          Operational Lifecycle Analytics
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Alert Performance, MTTA & MTTR Analytics
        </h1>
      </div>

      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>MEAN TIME TO ACKNOWLEDGE (MTTA)</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>12.0 min</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>MEAN TIME TO RESOLVE (MTTR)</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>4.2 hrs</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>FALSE POSITIVE RATE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>1.8%</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>DELIVERY SUCCESS RATE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7', marginTop: '2px' }}>99.2%</div>
        </div>
      </div>

      {/* Escalation Policy Ladder */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
          Active Critical Alert Escalation Policy Ladder
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          {[
            { tier: 'Tier 1: Triage Analyst', time: '0 - 15 min', status: 'DEFAULT_DISPATCH', color: '#38BDF8' },
            { tier: 'Tier 2: Functional Manager', time: '15 - 30 min', status: 'AUTO_ESCALATION', color: '#F59E0B' },
            { tier: 'Tier 3: Executive VP / CXO', time: '30 - 60 min', status: 'AUTO_ESCALATION', color: '#EF4444' },
            { tier: 'Tier 4: Board of Directors', time: '> 60 min', status: 'BOARDROOM_ESCALATION', color: '#A855F7' },
          ].map((item, idx) => (
            <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '16px', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 800, color: item.color }}>{item.status}</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>{item.tier}</div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>Timeout: {item.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
