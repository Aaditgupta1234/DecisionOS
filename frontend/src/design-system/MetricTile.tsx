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
        gap: '8px',
        padding: '20px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          {label}
        </span>
        {icon && <div style={{ color: '#64748B' }}>{icon}</div>}
      </div>

      <div style={{ fontSize: '2.2rem', fontWeight: 900, color: valueColor, lineHeight: 1.1 }}>
        {value}
      </div>

      {(sublabel || change) && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
          {change && (
            <span style={{ fontWeight: 800, color: changePositive ? '#10B981' : '#EF4444' }}>
              {change}
            </span>
          )}
          {sublabel && <span style={{ color: '#94A3B8' }}>{sublabel}</span>}
        </div>
      )}
    </Card>
  );
};
