import React from 'react';
import { useMotion } from '../motion/MotionProvider';

interface ShimmerBaseProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  className?: string;
  style?: React.CSSProperties;
}

export const ShimmerBase: React.FC<ShimmerBaseProps> = ({
  width = '100%',
  height = '16px',
  borderRadius = '6px',
  className = '',
  style,
}) => {
  const { isSuspended } = useMotion();

  return (
    <div
      className={`executive-shimmer-box ${isSuspended ? 'is-paused' : ''} ${className}`}
      style={{
        width,
        height,
        borderRadius,
        background: '#0D1117',
        position: 'relative',
        overflow: 'hidden',
        ...style,
      }}
    >
      <div className="shimmer-wave" />
    </div>
  );
};
