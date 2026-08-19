import React from 'react';
import { GitMerge, ShieldCheck, ArrowRight, CornerDownRight } from 'lucide-react';

export interface AttributionBranch {
  id: string;
  name: string;
  weightPct: number;
  impactScore?: string;
  confidenceScore: number;
  subFactors?: { name: string; pct: number }[];
}

interface Props {
  problemTitle?: string;
  branches?: AttributionBranch[];
  onSelectBranch?: (branch: AttributionBranch) => void;
  selectedBranchId?: string;
}

export const RootCauseTree: React.FC<Props> = ({
  problemTitle = 'Revenue Decline (-$218K / quarter)',
  branches = [
    {
      id: 'b1',
      name: 'Customer Retention Drop (Southeastern Routes)',
      weightPct: 48,
      impactScore: '-$104.6K',
      confidenceScore: 0.94,
      subFactors: [
        { name: 'Courier transit delay > 5 days', pct: 62 },
        { name: 'Late delivery review rating drop (2.1★)', pct: 38 },
      ],
    },
    {
      id: 'b2',
      name: 'Order Volume Stagnation',
      weightPct: 32,
      impactScore: '-$69.8K',
      confidenceScore: 0.91,
      subFactors: [
        { name: 'Ad channel saturation (Meta CAC +22%)', pct: 55 },
        { name: 'Cart abandonment on checkout step 2', pct: 45 },
      ],
    },
    {
      id: 'b3',
      name: 'Average Order Value Compression',
      weightPct: 20,
      impactScore: '-$43.6K',
      confidenceScore: 0.88,
      subFactors: [
        { name: 'Discount bundle promo expiry', pct: 70 },
        { name: 'Cross-sell attachment decrease', pct: 30 },
      ],
    },
  ],
  onSelectBranch,
  selectedBranchId,
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Root Node Header */}
      <div style={{
        background: '#0F172A',
        border: '1px solid #1E293B',
        borderRadius: '8px',
        padding: '12px 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#EF4444' }} />
          <span style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase' }}>Target Problem:</span>
          <span style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>{problemTitle}</span>
        </div>
        <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>Attribution Sum: 100%</span>
      </div>

      {/* Hierarchical Tree Branches */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {branches.map((b) => {
          const isSelected = selectedBranchId === b.id;

          return (
            <div
              key={b.id}
              onClick={() => onSelectBranch && onSelectBranch(b)}
              style={{
                background: isSelected ? 'rgba(56, 189, 248, 0.06)' : '#06080D',
                border: `1px solid ${isSelected ? '#38BDF8' : '#141C28'}`,
                borderRadius: '8px',
                padding: '14px 16px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <GitMerge size={14} color={isSelected ? '#38BDF8' : '#64748B'} />
                  <span style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>{b.name}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {b.impactScore && (
                    <span style={{ fontSize: '11.5px', color: '#F87171', fontWeight: 700 }}>
                      {b.impactScore}
                    </span>
                  )}
                  <span style={{ fontSize: '12px', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                    {b.weightPct}%
                  </span>
                </div>
              </div>

              {/* Attribution Weight Bar */}
              <div style={{ width: '100%', height: '4px', background: '#1E293B', borderRadius: '2px', overflow: 'hidden', marginBottom: '10px' }}>
                <div style={{ width: `${b.weightPct}%`, height: '100%', background: '#38BDF8' }} />
              </div>

              {/* Sub-factors */}
              {b.subFactors && b.subFactors.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', paddingLeft: '12px', borderLeft: '1px solid #1E293B', marginTop: '6px' }}>
                  {b.subFactors.map((sub, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: '#94A3B8' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <CornerDownRight size={10} color="#475569" />
                        <span>{sub.name}</span>
                      </div>
                      <span style={{ color: '#64748B', fontWeight: 600 }}>{sub.pct}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
