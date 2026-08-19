import React from 'react';
import { ShieldCheck, CheckCircle2, Hash } from 'lucide-react';

interface Props {
  traceId?: string;
  metricCount?: number;
  findingCount?: number;
  rootCauseCount?: number;
  recCount?: number;
}

export const TraceabilityBadge: React.FC<Props> = ({
  traceId = 'AI-2026-0818-0042',
  metricCount = 4,
  findingCount = 2,
  rootCauseCount = 1,
  recCount = 1,
}) => {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '8px',
      background: '#04070D',
      border: '1px solid #141D2B',
      borderRadius: '6px',
      padding: '6px 10px',
      fontSize: '10.5px',
      fontFamily: 'monospace',
      color: '#94A3B8',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
        <Hash size={12} color="#38BDF8" />
        <span>Response ID: <strong style={{ color: '#FFFFFF' }}>{traceId}</strong></span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10B981', fontWeight: 600 }}>
        <CheckCircle2 size={12} />
        <span>Grounding Verified: {metricCount} KPIs • {findingCount} Findings • {rootCauseCount} Cause • {recCount} Rec</span>
      </div>
    </div>
  );
};
