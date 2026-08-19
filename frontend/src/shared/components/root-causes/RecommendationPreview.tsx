import React from 'react';
import { CheckCircle2, TrendingUp, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  title?: string;
  expectedImpact?: string;
  confidence?: number;
  difficulty?: 'LOW' | 'MEDIUM' | 'HIGH';
  priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  description?: string;
}

export const RecommendationPreview: React.FC<Props> = ({
  title = 'Targeted Win-Back Campaign & Courier SLA Penalties',
  expectedImpact = '+$180K ARR',
  confidence = 91,
  difficulty = 'LOW',
  priority = 'HIGH',
  description = 'Automate personalized discount incentives for churn-risk customers in southeastern corridors while enforcing courier SLA delivery caps.',
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #0A121E 0%, #060B12 100%)',
      border: '1px solid rgba(16, 185, 129, 0.3)',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 12px 30px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(16, 185, 129, 0.1)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={14} color="#10B981" />
          <span style={{ fontSize: '11px', fontWeight: 800, color: '#10B981', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Recommended Next Action
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            fontSize: '9.5px',
            fontWeight: 800,
            color: priority === 'CRITICAL' ? '#EF4444' : '#38BDF8',
            background: 'rgba(56, 189, 248, 0.12)',
            padding: '2px 6px',
            borderRadius: '4px',
          }}>
            {priority} PRIORITY
          </span>
          <span style={{
            fontSize: '9.5px',
            fontWeight: 700,
            color: '#94A3B8',
            background: '#111622',
            padding: '2px 6px',
            borderRadius: '4px',
          }}>
            {difficulty} DIFFICULTY
          </span>
        </div>
      </div>

      <h4 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em', marginBottom: '8px' }}>
        {title}
      </h4>

      <p style={{ fontSize: '12.5px', color: '#CBD5E1', lineHeight: 1.5, marginBottom: '16px' }}>
        {description}
      </p>

      {/* Recovery Impact Pill & Action */}
      <div style={{
        background: 'rgba(16, 185, 129, 0.08)',
        border: '1px solid rgba(16, 185, 129, 0.25)',
        borderRadius: '8px',
        padding: '10px 14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div>
          <span style={{ display: 'block', fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 600 }}>
            Estimated Recovery Opportunity
          </span>
          <span style={{ fontSize: '16px', fontWeight: 800, color: '#10B981' }}>
            {expectedImpact}
          </span>
          <span style={{ fontSize: '11px', color: '#94A3B8', marginLeft: '6px' }}>({confidence}% confidence)</span>
        </div>

        <Link
          to="/recommendations"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#10B981',
            color: '#04060A',
            padding: '7px 14px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 800,
            textDecoration: 'none',
          }}
        >
          <span>Open Action Matrix</span>
          <ArrowRight size={13} />
        </Link>
      </div>
    </div>
  );
};
