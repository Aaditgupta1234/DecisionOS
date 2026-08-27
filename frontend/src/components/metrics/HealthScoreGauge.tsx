import React, { useEffect, useState, useRef } from 'react';
import { BusinessHealthStatus } from '../../types';
import { AnimatedCounter } from '../../design-system/motion/AnimatedCounter';
import { useMotion } from '../../design-system/motion/MotionProvider';
import { MOTION_LIMITS } from '../../design-system/motion/motionTokens';

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
  const { shouldReduceMotion } = useMotion();
  const [currentDashoffset, setCurrentDashoffset] = useState<number>(0);
  const isMountedRef = useRef<boolean>(false);

  const getStatusColor = (s: BusinessHealthStatus) => {
    switch (s) {
      case 'EXCELLENT':
      case 'HEALTHY':
        return '#10B981';
      case 'WATCH_LIST':
        return '#F59E0B';
      case 'AT_RISK':
      case 'CRITICAL':
        return '#EF4444';
      default:
        return '#38BDF8';
    }
  };

  const color = getStatusColor(status);
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const targetOffset = circumference - (Math.min(Math.max(score, 0), 100) / 100) * circumference;

  useEffect(() => {
    if (shouldReduceMotion) {
      setCurrentDashoffset(targetOffset);
      return;
    }

    if (!isMountedRef.current) {
      // Start from empty on first mount
      setCurrentDashoffset(circumference);
      const timer = setTimeout(() => {
        setCurrentDashoffset(targetOffset);
      }, 50);
      isMountedRef.current = true;
      return () => clearTimeout(timer);
    } else {
      // Live value update
      setCurrentDashoffset(targetOffset);
    }
  }, [targetOffset, circumference, shouldReduceMotion]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
      <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }} className="state-glow-health">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress circle with clamped 850ms duration */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={currentDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: `stroke-dashoffset ${MOTION_LIMITS.healthScoreDurationMs}ms cubic-bezier(0.16, 1, 0.3, 1)`,
            }}
          />
        </svg>

        {/* Central Score Text with Clamped Count-Up */}
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
            <AnimatedCounter value={score} durationMs={MOTION_LIMITS.healthScoreDurationMs} />
          </span>
          <span style={{ fontSize: '0.65rem', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '2px' }}>
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
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '4px',
              background: status === 'HEALTHY' || status === 'EXCELLENT' ? 'rgba(16, 185, 129, 0.15)' : status === 'WATCH_LIST' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color,
              border: `1px solid ${color}40`,
            }}
          >
            {status}
          </span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Composite Index</span>
        </div>
        {description && (
          <p style={{ fontSize: '0.85rem', color: '#94A3B8', maxWidth: '280px', lineHeight: 1.4, margin: 0 }}>
            {description}
          </p>
        )}
      </div>
    </div>
  );
};

