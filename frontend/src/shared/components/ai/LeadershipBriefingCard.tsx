import React from 'react';
import { Briefcase, CheckCircle2, ShieldAlert, Target } from 'lucide-react';

export const LeadershipBriefingCard: React.FC = () => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '24px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <Briefcase size={16} color="#38BDF8" />
        <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase', letterSpacing: '-0.01em' }}>
          Leadership Strategic Briefing Memo
        </h3>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
        {/* Board Talking Points */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
          <div style={{ fontSize: '11px', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase', marginBottom: '6px' }}>
            1. Board Executive Talking Points
          </div>
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: '#CBD5E1', lineHeight: 1.6 }}>
            <li>Business Health Score remains in top quartile (82/100 • EXCELLENT).</li>
            <li>Top-line growth remains healthy at +12.4% MoM across core product categories.</li>
            <li>Southeastern delivery delays represent an isolated operational fix with +$180K recovery.</li>
          </ul>
        </div>

        {/* 90-Day Execution Priorities */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
          <div style={{ fontSize: '11px', color: '#10B981', fontWeight: 800, textTransform: 'uppercase', marginBottom: '6px' }}>
            2. 90-Day Executive Priorities
          </div>
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '12px', color: '#CBD5E1', lineHeight: 1.6 }}>
            <li>Week 1–2: Deploy courier SLA contract penalties and automated win-back credit incentives.</li>
            <li>Week 3–4: Re-route secondary fulfillment hubs to eliminate peak dispatch backlogs.</li>
            <li>Month 2–3: Roll out AI cross-sell recommendation widgets on beauty & health checkout flows.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
