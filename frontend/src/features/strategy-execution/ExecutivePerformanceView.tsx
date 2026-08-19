import React from 'react';
import { Award, TrendingUp, CheckCircle2, DollarSign, Sparkles } from 'lucide-react';

export const ExecutivePerformanceView: React.FC = () => {
  const executives = [
    {
      rank: '#1 Leader',
      role: 'Chief Financial Officer (CFO)',
      decisions: 10,
      realizedArr: '$1.4M',
      accuracy: '89.5%',
      successRate: '90%',
      accountabilityScore: 95.1,
      badgeColor: '#10B981',
    },
    {
      rank: '#2 Leader',
      role: 'Chief Executive Officer (CEO)',
      decisions: 18,
      realizedArr: '$1.8M',
      accuracy: '91.2%',
      successRate: '84%',
      accountabilityScore: 92.4,
      badgeColor: '#38BDF8',
    },
    {
      rank: '#3 Leader',
      role: 'Chief Operating Officer (COO)',
      decisions: 14,
      realizedArr: '$2.1M',
      accuracy: '94.8%',
      successRate: '87%',
      accountabilityScore: 88.7,
      badgeColor: '#A855F7',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
          Executive Scorecards & Leadership Accountability
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Executive Performance & Scorecard Rankings
        </h1>
      </div>

      {/* Leader Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
        {executives.map((exec, idx) => (
          <div
            key={idx}
            style={{
              background: '#090D14',
              border: `1px solid ${exec.accountabilityScore >= 92 ? '#10B981' : '#1E293B'}`,
              borderRadius: '14px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 800, color: exec.badgeColor, background: 'rgba(15, 23, 42, 0.8)', padding: '3px 8px', borderRadius: '4px' }}>
                {exec.rank}
              </span>
              <span style={{ fontSize: '0.85rem', fontWeight: 900, color: '#10B981' }}>
                Score: {exec.accountabilityScore}
              </span>
            </div>

            <div style={{ fontSize: '1.1rem', fontWeight: 900, color: '#FFFFFF' }}>{exec.role}</div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>REALIZED VALUE</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>{exec.realizedArr}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>FORECAST ACCURACY</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>{exec.accuracy}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>DECISIONS APPROVED</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>{exec.decisions}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>SUCCESS RATE</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>{exec.successRate}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
