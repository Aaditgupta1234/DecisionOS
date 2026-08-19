import React from 'react';
import { BarChart3, TrendingUp, DollarSign, Target, CheckCircle2 } from 'lucide-react';

export const BenefitsRealizationView: React.FC = () => {
  const realizationMetrics = [
    { label: 'Annual Recurring Revenue (ARR)', expected: '+$2,800,000', actual: '+$2,500,000', score: '89.3%', color: '#10B981' },
    { label: 'Customer Retention Rate Lift', expected: '+12.5 pts', actual: '+11.0 pts', score: '88.0%', color: '#38BDF8' },
    { label: 'Delivery Latency Reduction', expected: '-2.0 Days', actual: '-2.0 Days', score: '100.0%', color: '#A855F7' },
    { label: 'Systemic Risk Reduction', expected: '-12.0 pts', actual: '-10.5 pts', score: '87.5%', color: '#F59E0B' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Empirical Benefits Realization & Auditing
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Portfolio Benefits Realization
        </h1>
      </div>

      {/* Realization Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {realizationMetrics.map((m, idx) => (
          <div
            key={idx}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '14px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF' }}>{m.label}</span>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: m.color, background: 'rgba(15, 23, 42, 0.8)', padding: '3px 8px', borderRadius: '4px' }}>
                {m.score} Realized
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>EXPECTED VALUE</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#94A3B8', marginTop: '2px' }}>{m.expected}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>REALIZED VALUE</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 900, color: m.color, marginTop: '2px' }}>{m.actual}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
