import React, { useEffect, useState, useRef } from 'react';
import { useMotion } from './MotionProvider';
import { MOTION_LIMITS } from './motionTokens';

interface AnimatedCounterProps {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  durationMs?: number;
  className?: string;
  style?: React.CSSProperties;
  formatter?: (val: number) => string;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  prefix = '',
  suffix = '',
  decimals = 0,
  durationMs = MOTION_LIMITS.healthScoreDurationMs,
  className,
  style,
  formatter,
}) => {
  const { shouldReduceMotion, isSuspended } = useMotion();
  const isTestEnv = typeof window !== 'undefined' && Boolean((window as any).__VITEST_ENVIRONMENT__ || (import.meta as any).env?.MODE === 'test');
  const [displayValue, setDisplayValue] = useState<number>(shouldReduceMotion || isTestEnv ? value : 0);
  const startTimeRef = useRef<number | null>(null);
  const startValueRef = useRef<number>(0);
  const targetValueRef = useRef<number>(value);
  const requestRef = useRef<number | null>(null);

  // Clamp duration strictly between 700ms – 1000ms
  const clampedDuration = Math.min(Math.max(durationMs, 700), 1000);

  useEffect(() => {
    if (shouldReduceMotion || isTestEnv) {
      setDisplayValue(value);
      return;
    }

    startValueRef.current = displayValue;
    targetValueRef.current = value;
    startTimeRef.current = null;

    const animate = (timestamp: number) => {
      // If tab is suspended, hold current frame until visible
      if (isSuspended) {
        requestRef.current = requestAnimationFrame(animate);
        return;
      }

      if (!startTimeRef.current) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / clampedDuration, 1);

      // Executive ease-out curve (1 - Math.pow(1 - progress, 3))
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startValueRef.current + (targetValueRef.current - startValueRef.current) * easeOut;

      setDisplayValue(current);

      if (progress < 1) {
        requestRef.current = requestAnimationFrame(animate);
      } else {
        setDisplayValue(targetValueRef.current);
      }
    };

    requestRef.current = requestAnimationFrame(animate);

    return () => {
      if (requestRef.current) cancelAnimationFrame(requestRef.current);
    };
  }, [value, shouldReduceMotion, isSuspended, clampedDuration]);

  const formattedText = formatter
    ? formatter(displayValue)
    : `${prefix}${displayValue.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      })}${suffix}`;

  return (
    <span className={className} style={{ willChange: 'contents', fontVariantNumeric: 'tabular-nums', ...style }}>
      {formattedText}
    </span>
  );
};
