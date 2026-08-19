import React from 'react';
import { ShieldCheck, ShieldAlert, Zap, Lock } from 'lucide-react';

interface Props {
  highConfidence?: string;
  mediumConfidence?: string;
  lowConfidence?: string;
  totalOpportunity?: string;
}

export const RecoveryConfidenceBreakdown: React.FC<Props> = ({
  highConfidence = '+$220K ARR (Guaranteed Upside)',
  mediumConfidence = '+$180K ARR (Likely Upside)',
  lowConfidence = '+$80K ARR (Speculative Upside)',
  totalOpportunity = '+$480K ARR Total',
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <h4 style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.04em', margin: 0 }}>
          Recovery Upside Confidence Segmentation
        </h4>
        <span style={{ fontSize: '11px', fontWeight: 800, color: '#10B981' }}>
          {totalOpportunity}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#10B981', fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            <Lock size={12} />
            <span>High Confidence (&gt;90%)</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {highConfidence}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Courier SLA & Win-Back core</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#38BDF8', fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            <Zap size={12} />
            <span>Medium Confidence (75–90%)</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {mediumConfidence}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Multi-hub dispatch balancing</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#F59E0B', fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            <ShieldAlert size={12} />
            <span>Low / Speculative (&lt;75%)</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {lowConfidence}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Cross-sell attachment beta</span>
        </div>
      </div>
    </div>
  );
};
