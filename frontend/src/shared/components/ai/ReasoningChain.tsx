import React from 'react';
import { GitMerge, ArrowDown, ShieldCheck } from 'lucide-react';

interface Props {
  steps?: string[];
  confidence?: number;
}

export const ReasoningChain: React.FC<Props> = ({
  steps = [
    'Customer Retention rate fell from 90.1% → 85.8% (-4.3% variance)',
    'Retention decline was isolated specifically to Southeastern logistics corridors',
    'Courier transit times exceeding 5 days triggered acute 1-star reviews (2.1★ avg)',
    'Dissatisfied customers exhibited 48% higher churn velocity & pre-delivery cancellations',
    'Compounded repeat purchase drop created -$218K / quarter top-line exposure',
  ],
  confidence = 91,
}) => {
  return (
    <div style={{
      background: 'rgba(56, 189, 248, 0.04)',
      border: '1px solid rgba(56, 189, 248, 0.2)',
      borderRadius: '8px',
      padding: '14px 16px',
      margin: '12px 0',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <GitMerge size={14} color="#38BDF8" />
          <span style={{ fontSize: '11px', fontWeight: 800, color: '#38BDF8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Why This Answer? — Deterministic Reasoning Chain
          </span>
        </div>

        <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700 }}>
          {confidence}% Statistical DAG Confidence
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {steps.map((step, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '12px', color: '#E2E8F0' }}>
            <span style={{
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              background: '#111827',
              border: '1px solid #1E293B',
              color: '#38BDF8',
              fontSize: '10px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginTop: '1px',
            }}>
              {idx + 1}
            </span>
            <span style={{ lineHeight: 1.4 }}>{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
