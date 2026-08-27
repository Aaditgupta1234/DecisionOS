import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { useMotion } from './MotionProvider';
import { MOTION_LIMITS, EASING, SPRING } from './motionTokens';

interface MotionCardProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children?: React.ReactNode;
  interactive?: boolean;
  elevation?: 'flat' | 'subtle' | 'floating';
}

export const MotionCard: React.FC<MotionCardProps> = ({
  children,
  className = '',
  interactive = true,
  elevation = 'subtle',
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  const hoverProps = interactive && !shouldReduceMotion
    ? {
        whileHover: {
          y: -3,
          scale: MOTION_LIMITS.cardHoverScale,
          transition: { duration: 0.16, ease: EASING.executive },
        },
        whileTap: {
          scale: 0.995,
          transition: { duration: 0.1 },
        },
      }
    : {};

  return (
    <motion.div
      {...hoverProps}
      className={`executive-motion-card ${interactive ? 'is-interactive' : ''} ${className}`}
      style={{
        willChange: interactive ? 'transform' : 'auto',
        ...style,
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
};
