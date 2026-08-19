import React from 'react';
import { Zap, ArrowRight, ShieldCheck } from 'lucide-react';

export interface PriorityItem {
  id: string;
  rank: number;
  title: string;
  recoveryARR: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  difficulty: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence: number;
  rootCauseId?: string;
}

interface Props {
  items?: PriorityItem[];
  onSelectAction?: (item: PriorityItem) => void;
}

export const PriorityRankingBanner: React.FC<Props> = ({
  items = [
    {
      id: 'rec_1',
      rank: 1,
      title: 'Targeted Win-Back Campaign & Courier SLA Penalties',
      recoveryARR: '+$180K ARR',
      priority: 'HIGH',
      difficulty: 'LOW',
      confidence: 92,
      rootCauseId: 'rc_1',
    },
    {
      id: 'rec_2',
      rank: 2,
      title: 'Dynamic Dispatch Load-Balancing Across Secondary Hubs',
      recoveryARR: '+$140K ARR',
      priority: 'HIGH',
      difficulty: 'MEDIUM',
      confidence: 90,
      rootCauseId: 'rc_2',
    },
    {
      id: 'rec_3',
      rank: 3,
      title: 'Automated Post-Purchase Cross-Sell Recommendation Engine',
      recoveryARR: '+$85K ARR',
      priority: 'MEDIUM',
      difficulty: 'LOW',
      confidence: 88,
      rootCauseId: 'rc_3',
    },
  ],
  onSelectAction,
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #0B111A 0%, #06090F 100%)',
      border: '1px solid #1E293B',
      borderRadius: '12px',
      padding: '18px 20px',
      marginBottom: '24px',
      boxShadow: '0 12px 30px rgba(0, 0, 0, 0.6)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
          <Zap size={15} color="#F59E0B" />
          <span style={{ fontSize: '11px', fontWeight: 800, color: '#E2E8F0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Executive Priority Ranking — Top 3 Recommended Actions
          </span>
        </div>
        <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>
          Ranked by ROI Velocity & Feasibility
        </span>
      </div>

      {/* 3 Ranked Action Chips */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
        {items.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelectAction && onSelectAction(item)}
            style={{
              background: '#04060A',
              border: '1px solid #141C28',
              borderRadius: '8px',
              padding: '12px 14px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 900,
                  color: '#F59E0B',
                  background: 'rgba(245, 158, 11, 0.12)',
                  border: '1px solid rgba(245, 158, 11, 0.28)',
                  padding: '1px 6px',
                  borderRadius: '4px',
                }}>
                  RANK #{item.rank}
                </span>

                <span style={{ fontSize: '10px', color: '#64748B', fontWeight: 600 }}>
                  {item.difficulty} Difficulty
                </span>
              </div>

              <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.35, marginBottom: '8px' }}>
                {item.title}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #0F1622', paddingTop: '8px', marginTop: '4px' }}>
              <span style={{ fontSize: '13px', fontWeight: 800, color: '#10B981' }}>
                {item.recoveryARR}
              </span>
              <span style={{ fontSize: '10px', color: '#38BDF8', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                <ShieldCheck size={11} />
                <span>{item.confidence}%</span>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
