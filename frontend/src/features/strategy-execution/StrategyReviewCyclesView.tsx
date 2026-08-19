import React from 'react';
import { History, CheckCircle2, TrendingUp, Sparkles, BookOpen } from 'lucide-react';

export const StrategyReviewCyclesView: React.FC = () => {
  const reviews = [
    {
      title: 'Q4 Enterprise Strategy Review & Fiduciary Close',
      date: 'Completed 5 days ago',
      inits: 42,
      realizedArr: '$2.5M',
      lessons: [
        'Carrier SLA penalties must be accompanied by dynamic load rebalancing to prevent courier attrition.',
        'Customer win-back tokens achieved 3.4x higher conversion when sent via delivery delay webhooks rather than email.',
        'Monte Carlo 50K iterations bounded reality with 95.2% accuracy.',
      ],
    },
    {
      title: 'Q3 Enterprise Mid-Year Review',
      date: 'Completed 95 days ago',
      inits: 36,
      realizedArr: '$1.95M',
      lessons: [
        'Early identification of dispatch bottlenecks in Secondary Hubs accelerated intervention by 2 weeks.',
      ],
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Institutional Learning & Governance Timeline
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Quarterly Strategy Review Cycles
        </h1>
      </div>

      {/* Reviews List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {reviews.map((rev, idx) => (
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
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>{rev.title}</h3>
              <span style={{ fontSize: '0.75rem', color: '#64748B' }}>{rev.date}</span>
            </div>

            <div style={{ display: 'flex', gap: '16px', fontSize: '0.82rem' }}>
              <span style={{ color: '#94A3B8' }}>Initiatives Audited: <strong style={{ color: '#FFFFFF' }}>{rev.inits}</strong></span>
              <span style={{ color: '#94A3B8' }}>Delivered Value: <strong style={{ color: '#10B981' }}>{rev.realizedArr}</strong></span>
            </div>

            <div>
              <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#38BDF8', marginBottom: '6px' }}>
                Institutional Lessons Learned:
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {rev.lessons.map((lesson, lIdx) => (
                  <div key={lIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.8rem', color: '#F1F5F9' }}>
                    <span style={{ color: '#10B981' }}>•</span>
                    <span>{lesson}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
