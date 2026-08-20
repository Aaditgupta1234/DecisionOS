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
        gap: '4px',
        padding: '14px 16px',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
        border: '1px solid #14171E',
        borderRadius: '10px',
        boxShadow: '0 4px 14px rgba(0,0,0,0.35)',
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
        <span style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          {label}
        </span>
        {icon && <div style={{ color: '#64748B' }}>{icon}</div>}
      </div>

      <div style={{ fontSize: '1.55rem', fontWeight: 900, color: valueColor, lineHeight: 1.15, letterSpacing: '-0.02em', margin: '2px 0 1px 0' }}>
        {value}
      </div>

      {(sublabel || change) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.72rem' }}>
          {change && (
            <span
              style={{
                fontWeight: 800,
                color: changePositive ? '#10B981' : '#EF4444',
                background: changePositive ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                padding: '1px 5px',
                borderRadius: '3px',
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
