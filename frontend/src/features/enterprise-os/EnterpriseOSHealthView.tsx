import React from 'react';
import { Award, ShieldCheck, CheckCircle2, TrendingUp, Activity, Cpu, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const EnterpriseOSHealthView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Platform-Wide Governance & Reliability Index
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Enterprise Operating Score & Reliability Health
        </h1>
      </div>

      {/* Hero Big Widget */}
      <div style={{ background: '#090D14', border: '1px solid #10B981', borderRadius: '16px', padding: '32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <div style={{ fontSize: '0.8rem', color: '#10B981', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            ENTERPRISE OPERATING SCORE
          </div>
          <div style={{ fontSize: '3.6rem', fontWeight: 900, color: '#FFFFFF', lineHeight: 1, marginTop: '8px' }}>
            94.8 <span style={{ fontSize: '1.4rem', color: '#64748B' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '0.9rem', color: '#10B981', fontWeight: 800, marginTop: '8px' }}>
            Grade A+ Enterprise Decision Intelligence Platform
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px', minWidth: '320px' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px 16px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>GOVERNANCE HEALTH</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>98.4%</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px 16px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>POLICY COMPLIANCE</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>99.1%</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px 16px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>WORKFLOW SUCCESS</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>97.2%</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px 16px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B' }}>FORECAST ACCURACY</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F59E0B', marginTop: '2px' }}>95.2%</div>
          </div>
        </div>
      </div>
    </div>
  );
};
