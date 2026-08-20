import React from 'react';
import { Card } from './Card';

interface MetricTileProps {
  label: string;
  value: string | number;
  sublabel?: string;
  change?: string;
  changePositive?: boolean;
  valueColor?: string;
  icon?: React.ReactNode;
  onClick?: () => void;
}

export const MetricTile: React.FC<MetricTileProps> = ({
  label,
  value,
  sublabel,
  change,
  changePositive = true,
  valueColor = '#FFFFFF',
  icon,
  onClick,
}) => {
  return (
    <Card
      onClick={onClick}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        padding: '22px 24px',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
        border: '1px solid #14171E',
        borderRadius: '14px',
      }}
    >
      {/* Top subtle highlight shimmer */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: '15%',
          right: '15%',
          height: '1px',
          background: 'linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.4), transparent)',
        }}
      />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          {label}
        </span>
        {icon && <div style={{ color: '#64748B' }}>{icon}</div>}
      </div>

      <div style={{ fontSize: '2.3rem', fontWeight: 900, color: valueColor, lineHeight: 1.1, letterSpacing: '-0.03em', margin: '4px 0 2px 0' }}>
        {value}
      </div>

      {(sublabel || change) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.76rem' }}>
          {change && (
            <span
              style={{
                fontWeight: 800,
                color: changePositive ? '#10B981' : '#EF4444',
                background: changePositive ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                padding: '1px 6px',
                borderRadius: '4px',
                border: `1px solid ${changePositive ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)'}`,
              }}
            >
              {change}
            </span>
          )}
          {sublabel && <span style={{ color: '#94A3B8' }}>{sublabel}</span>}
        </div>
      )}
    </Card>
  );
};
