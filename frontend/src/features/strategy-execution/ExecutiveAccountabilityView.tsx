import React from 'react';
import { ShieldCheck, CheckCircle2, Award, Clock } from 'lucide-react';

export const ExecutiveAccountabilityView: React.FC = () => {
  const records = [
    {
      role: 'Chief Operating Officer (COO)',
      decision: 'Approved 15% courier SLA billing penalties on bottom 20% latency carriers.',
      expected: '+$124,000 ARR • +11.0 Health',
      actual: '+$118,000 ARR • +10.5 Health',
      accuracy: '95.2%',
      date: '45 days ago',
    },
    {
      role: 'Chief Executive Officer (CEO)',
      decision: 'Ratified Q4 Strategic Plan committing $25.8K capital to Southeastern distribution node rebalancing.',
      expected: '+$124,000 ARR • 85.0 Health',
      actual: '+$118,000 ARR • 85.0 Health',
      accuracy: '95.2%',
      date: '60 days ago',
    },
    {
      role: 'Chief Financial Officer (CFO)',
      decision: 'Allocated $15,000 courier penalty recovery surplus into Q1 marketing acquisition reserves.',
      expected: '$18,400 Reserve • 4.8x ROI',
      actual: '$18,400 Reserve • 4.6x ROI',
      accuracy: '95.8%',
      date: '30 days ago',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
          Executive Governance & Fiduciary Audit
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Executive Decision Ledger & Accountability
        </h1>
      </div>

      {/* Decision Records List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {records.map((r, idx) => (
          <div
            key={idx}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '12px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#38BDF8' }}>{r.role}</span>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                ✓ {r.accuracy} Accuracy
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#FFFFFF', fontWeight: 600, margin: 0 }}>{r.decision}</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '10px 14px', borderRadius: '6px', fontSize: '0.75rem' }}>
              <div>
                <span style={{ color: '#64748B' }}>Expected Impact: </span>
                <span style={{ color: '#94A3B8', fontWeight: 700 }}>{r.expected}</span>
              </div>
              <div>
                <span style={{ color: '#64748B' }}>Realized Impact: </span>
                <span style={{ color: '#10B981', fontWeight: 800 }}>{r.actual}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
