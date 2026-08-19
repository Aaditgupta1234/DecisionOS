import React, { useState } from 'react';
import { Target, CheckCircle2, Clock, DollarSign, UserCheck, AlertCircle, Plus } from 'lucide-react';

export const BoardDirectivesPanel: React.FC = () => {
  const [directives, setDirectives] = useState([
    {
      id: 'DIR-01',
      title: 'Enforce Courier SLA Penalties in Southeastern Hubs',
      desc: 'Automate 15% billing penalty on bottom 20% latency couriers across all regional hubs.',
      owner: 'COO / VP Logistics',
      dueDate: 'In 12 days',
      status: 'COMPLETED',
      expectedArr: '+$124,000',
      actualArr: '+$118,000',
      achievement: '95.2%',
    },
    {
      id: 'DIR-02',
      title: 'Deploy Customer Win-Back Incentive Campaign',
      desc: 'Issue automated discount credits and proactive notification webhooks to delayed accounts.',
      owner: 'VP Customer Success',
      dueDate: 'In 34 days',
      status: 'IN_PROGRESS',
      expectedArr: '+$82,000',
      actualArr: 'Pending ($42K realized)',
      achievement: '51.2%',
    },
    {
      id: 'DIR-03',
      title: 'Northern Corridor Distribution Center Expansion',
      desc: 'Replicate proven courier rebalancing model into adjacent Northern shipping zones.',
      owner: 'CEO / Executive Leadership',
      dueDate: 'In 85 days',
      status: 'OPEN',
      expectedArr: '+$134,000',
      actualArr: 'Pending launch',
      achievement: '0.0%',
    },
  ]);

  return (
    <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
            Fiduciary Accountability & Realization
          </div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF', margin: '2px 0 0 0' }}>
            Board Directives & Action Tracker
          </h2>
        </div>

        <span style={{ fontSize: '0.78rem', color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', padding: '4px 10px', borderRadius: '20px', fontWeight: 800 }}>
          Avg Realization: 95.2%
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {directives.map((dir) => (
          <div
            key={dir.id}
            style={{
              padding: '16px',
              borderRadius: '8px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid #1E293B',
              display: 'flex',
              flexDirection: 'column',
              gap: '10px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 6px', borderRadius: '4px' }}>
                  {dir.id}
                </span>
                <span style={{ fontSize: '0.92rem', fontWeight: 700, color: '#FFFFFF' }}>{dir.title}</span>
              </div>
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 800,
                  padding: '3px 8px',
                  borderRadius: '12px',
                  background: dir.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : dir.status === 'IN_PROGRESS' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                  color: dir.status === 'COMPLETED' ? '#10B981' : dir.status === 'IN_PROGRESS' ? '#38BDF8' : '#F59E0B',
                }}
              >
                {dir.status}
              </span>
            </div>

            <div style={{ fontSize: '0.8rem', color: '#94A3B8', lineHeight: 1.4 }}>{dir.desc}</div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', background: 'rgba(9, 13, 20, 0.6)', border: '1px solid #1E293B', padding: '10px', borderRadius: '6px' }}>
              <div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>EXECUTIVE OWNER</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9', marginTop: '2px' }}>{dir.owner}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>EXPECTED ARR</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#38BDF8', marginTop: '2px' }}>{dir.expectedArr}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>ACTUAL REALIZED</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#10B981', marginTop: '2px' }}>{dir.actualArr}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.68rem', color: '#64748B' }}>ACHIEVEMENT</div>
                <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>{dir.achievement}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
