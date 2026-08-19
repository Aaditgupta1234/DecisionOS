import React from 'react';
import { TrendingDown, TrendingUp } from 'lucide-react';

export const RecoveryWaterfallActual: React.FC = () => {
  const steps = [
    { label: 'Initial Quarterly Exposure', amount: '-$218K', isNeg: true },
    { label: 'Win-Back Realized ARR', amount: '+$124K', isPos: true },
    { label: 'Dispatch Optimization (In Progress)', amount: '+$0K', isNeutral: true },
    { label: 'Cross-Sell Engine (Pending)', amount: '+$0K', isNeutral: true },
    { label: 'Net Realized Recovery', amount: '+$124K ARR', isTotal: true },
  ];

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Realized Recovery Financial Bridge Waterfall
          </h4>
          <span style={{ fontSize: '11px', color: '#64748B' }}>
            Closing the loop from detected exposure to captured bottom-line value
          </span>
        </div>

        <span style={{ fontSize: '11.5px', fontWeight: 800, color: '#10B981' }}>
          +$124K Net Realized
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: '10px',
        alignItems: 'stretch',
      }}>
        {steps.map((step, idx) => {
          return (
            <div
              key={idx}
              style={{
                background: step.isNeg ? 'rgba(239, 68, 68, 0.08)' : step.isTotal ? 'rgba(16, 185, 129, 0.12)' : '#05070B',
                border: `1px solid ${step.isNeg ? 'rgba(239, 68, 68, 0.3)' : step.isTotal ? 'rgba(16, 185, 129, 0.4)' : '#141C28'}`,
                borderRadius: '8px',
                padding: '12px',
                textAlign: 'center',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                minHeight: '85px',
              }}
            >
              <span style={{ fontSize: '10.5px', color: '#94A3B8', fontWeight: 600, lineHeight: 1.2 }}>
                {step.label}
              </span>

              <div style={{
                fontSize: step.isTotal ? '15px' : '13.5px',
                fontWeight: 800,
                color: step.isNeg ? '#EF4444' : step.isTotal || step.isPos ? '#10B981' : '#64748B',
                marginTop: '4px',
              }}>
                {step.amount}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
