import React from 'react';
import { Calendar, Clock, TrendingUp, AlertCircle, ShieldCheck } from 'lucide-react';

interface Props {
  targetDate?: string;
  predictedCompletion?: string;
  velocityRisk?: 'LOW' | 'MEDIUM' | 'HIGH';
  progressVelocityPct?: number;
}

export const ExecutionForecastCard: React.FC<Props> = ({
  targetDate = 'Sep 15, 2026',
  predictedCompletion = 'Sep 22, 2026 (7 Days Variance)',
  velocityRisk = 'LOW',
  progressVelocityPct = 85,
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '18px 20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Clock size={15} color="#38BDF8" />
          <span style={{ fontSize: '11px', fontWeight: 800, color: '#38BDF8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Forecasted Completion Intelligence
          </span>
        </div>

        <span style={{
          fontSize: '10px',
          fontWeight: 800,
          color: velocityRisk === 'LOW' ? '#10B981' : velocityRisk === 'MEDIUM' ? '#F59E0B' : '#EF4444',
          background: 'rgba(255, 255, 255, 0.04)',
          padding: '2px 7px',
          borderRadius: '4px',
        }}>
          VELOCITY RISK: {velocityRisk}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '10px' }}>
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px' }}>
          <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase' }}>Target Commitment Date</span>
          <div style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {targetDate}
          </div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px' }}>
          <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase' }}>Predicted Completion</span>
          <div style={{ fontSize: '14px', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>
            {predictedCompletion}
          </div>
        </div>
      </div>

      <p style={{ fontSize: '11.5px', color: '#94A3B8', margin: 0, lineHeight: 1.4 }}>
        Based on historical milestone completion rates, current velocity tracks at <strong>{progressVelocityPct}%</strong> of schedule baseline.
      </p>
    </div>
  );
};
