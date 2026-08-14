import React from 'react';
import { BusinessHealthStatus } from '../../types';

interface HealthScoreGaugeProps {
  score: number;
  status: BusinessHealthStatus;
  description?: string;
  size?: number;
}

export const HealthScoreGauge: React.FC<HealthScoreGaugeProps> = ({
  score,
  status,
  description,
  size = 130,
}) => {
  const getStatusColor = (s: BusinessHealthStatus) => {
    switch (s) {
      case 'EXCELLENT':
      case 'HEALTHY':
        return 'var(--color-success)';
      case 'WATCH_LIST':
        return 'var(--color-warning)';
      case 'AT_RISK':
      case 'CRITICAL':
        return 'var(--color-danger)';
      default:
        return 'var(--color-primary-light)';
    }
  };

  const color = getStatusColor(status);
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="var(--bg-surface-elevated)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: 'stroke-dashoffset 0.8s ease-in-out' }}
          />
        </svg>

        {/* Central Score Text */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <span style={{ fontSize: '2rem', fontWeight: 800, color: '#ffffff', lineHeight: 1 }}>
            {score}
          </span>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            / 100
          </span>
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span
            className={`badge ${
              status === 'HEALTHY' || status === 'EXCELLENT'
                ? 'badge-success'
                : status === 'WATCH_LIST'
                ? 'badge-warning'
                : 'badge-danger'
            }`}
          >
            {status}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Composite Index</span>
        </div>
        {description && (
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '280px', lineHeight: 1.4 }}>
            {description}
          </p>
        )}
      </div>
    </div>
  );
};
