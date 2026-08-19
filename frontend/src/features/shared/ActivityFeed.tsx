import React from 'react';
import { Activity, Sparkles, CheckCircle2, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ActivityFeed: React.FC = () => {
  const activities = [
    {
      id: 'act-1',
      title: 'Initiative INIT-2026-051 Realized +$312,000 ARR',
      time: '12m ago',
      type: 'OUTCOME',
      icon: <TrendingUp size={14} color="#10B981" />,
      route: '/strategy-execution',
    },
    {
      id: 'act-2',
      title: 'Autonomous Strategy Agent dispatched Scenario SIM-018',
      time: '34m ago',
      type: 'AGENT',
      icon: <Sparkles size={14} color="#A855F7" />,
      route: '/agents',
    },
    {
      id: 'act-3',
      title: 'Q1 Boardroom Strategic Briefing Deck Approved by CEO',
      time: '2h ago',
      type: 'GOVERNANCE',
      icon: <ShieldCheck size={14} color="#38BDF8" />,
      route: '/reports',
    },
    {
      id: 'act-4',
      title: 'SaaS Capital Benchmark Index data refreshed (98% freshness)',
      time: '4h ago',
      type: 'BENCHMARK',
      icon: <Activity size={14} color="#F59E0B" />,
      route: '/competitive-intelligence',
    },
  ];

  return (
    <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>Platform Activity Feed</span>
        <span style={{ fontSize: '0.72rem', color: '#10B981', fontWeight: 700 }}>● LIVE PULSE</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {activities.map((item) => (
          <Link
            key={item.id}
            to={item.route}
            style={{
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid #1E293B',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              textDecoration: 'none',
              transition: 'border-color 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>{item.icon}</div>
              <span style={{ fontSize: '0.8rem', color: '#F1F5F9', fontWeight: 600 }}>{item.title}</span>
            </div>
            <span style={{ fontSize: '0.7rem', color: '#64748B' }}>{item.time}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};
