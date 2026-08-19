import React from 'react';
import { TrendingUp, ShieldCheck, ArrowRight, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  title: string;
  expectedImpact: string;
  confidence?: number;
  recommendedAction: string;
  affectedKpi: string;
  recId?: string;
}

export const OpportunityCard: React.FC<Props> = ({
  title,
  expectedImpact,
  confidence = 92,
  recommendedAction,
  affectedKpi,
  recId = 'rec_1',
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '10px',
      padding: '16px 18px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <TrendingUp size={14} color="#10B981" />
            <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#10B981', textTransform: 'uppercase' }}>
              Strategic Opportunity
            </span>
          </div>

          <span style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '3px' }}>
            <ShieldCheck size={12} />
            <span>{confidence}% Confidence</span>
          </span>
        </div>

        <h4 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', margin: '0 0 6px' }}>
          {title}
        </h4>

        <p style={{ fontSize: '12px', color: '#CBD5E1', lineHeight: 1.45, marginBottom: '12px' }}>
          {recommendedAction}
        </p>
      </div>

      <div style={{ borderTop: '1px solid #141C28', paddingTop: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <span style={{ fontSize: '10px', color: '#64748B', display: 'block', textTransform: 'uppercase' }}>Expected Upside</span>
          <span style={{ fontSize: '14px', fontWeight: 800, color: '#10B981' }}>{expectedImpact}</span>
        </div>

        <Link
          to="/recommendations"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            background: '#111622',
            border: '1px solid #1F2738',
            color: '#38BDF8',
            padding: '5px 10px',
            borderRadius: '5px',
            fontSize: '11px',
            fontWeight: 700,
            textDecoration: 'none',
          }}
        >
          <span>View Action</span>
          <ArrowRight size={11} />
        </Link>
      </div>
    </div>
  );
};
