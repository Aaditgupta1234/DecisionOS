import React from 'react';
import { TrendingDown, TrendingUp, ArrowRight, ShieldCheck } from 'lucide-react';

interface WaterfallStep {
  label: string;
  amount: number;
  displayAmount: string;
  isNegative?: boolean;
  isTotal?: boolean;
}

interface Props {
  currentLoss?: string;
  netRecovery?: string;
}

export const RecoveryWaterfallCard: React.FC<Props> = ({
  currentLoss = '-$218K / Qtr',
  netRecovery = '+$480K ARR',
}) => {
  const steps: WaterfallStep[] = [
    { label: 'Current Exposure', amount: -218, displayAmount: '-$218K', isNegative: true },
    { label: 'Win-Back Action', amount: 180, displayAmount: '+$180K' },
    { label: 'Dispatch Load-Balance', amount: 140, displayAmount: '+$140K' },
    { label: 'Cross-Sell Engine', amount: 85, displayAmount: '+$85K' },
    { label: 'Payment Optimization', amount: 75, displayAmount: '+$75K' },
    { label: 'Net Recovery Potential', amount: 480, displayAmount: '+$480K ARR', isTotal: true },
  ];

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
            Financial Recovery Potential Waterfall
          </h3>
          <span style={{ fontSize: '11px', color: '#64748B' }}>
            Bridging current diagnostic exposure to net ARR growth through prioritized initiatives
          </span>
        </div>

        <div style={{
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10B981',
          padding: '4px 12px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 800,
        }}>
          Total Upside: {netRecovery}
        </div>
      </div>

      {/* Waterfall Visual Bridge */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: '10px',
        alignItems: 'flex-end',
      }}>
        {steps.map((step, idx) => {
          const isNeg = step.isNegative;
          const isTot = step.isTotal;

          return (
            <div
              key={idx}
              style={{
                background: isNeg ? 'rgba(239, 68, 68, 0.08)' : isTot ? 'rgba(16, 185, 129, 0.15)' : '#05070B',
                border: `1px solid ${isNeg ? 'rgba(239, 68, 68, 0.3)' : isTot ? 'rgba(16, 185, 129, 0.4)' : '#141C28'}`,
                borderRadius: '8px',
                padding: '12px 10px',
                textAlign: 'center',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: '90px',
              }}
            >
              <span style={{ fontSize: '10px', color: '#94A3B8', fontWeight: 600, lineHeight: 1.2 }}>
                {step.label}
              </span>

              <div style={{
                fontSize: isTot ? '15px' : '13px',
                fontWeight: 800,
                color: isNeg ? '#EF4444' : '#10B981',
                marginTop: '6px',
              }}>
                {step.displayAmount}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
