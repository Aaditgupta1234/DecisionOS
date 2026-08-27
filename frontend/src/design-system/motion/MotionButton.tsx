import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { useMotion } from './MotionProvider';
import { MOTION_LIMITS, EASING } from './motionTokens';

interface MotionButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  children?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export const MotionButton: React.FC<MotionButtonProps> = ({
  children,
  className = '',
  variant = 'primary',
  icon,
  iconPosition = 'right',
  disabled,
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  const hoverAnimation = !disabled && !shouldReduceMotion
    ? {
        whileHover: {
          scale: MOTION_LIMITS.buttonHoverScale,
          transition: { duration: 0.14, ease: EASING.micro },
        },
        whileTap: {
          scale: 0.98,
          transition: { duration: 0.08 },
        },
      }
    : {};

  return (
    <motion.button
      {...hoverAnimation}
      disabled={disabled}
      className={`executive-motion-btn btn-${variant} ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        willChange: 'transform',
        ...style,
      }}
      {...props}
    >
      {icon && iconPosition === 'left' && (
        <span className="btn-icon-wrapper left">{icon}</span>
      )}
      {children}
      {icon && iconPosition === 'right' && (
        <span className="btn-icon-wrapper right">{icon}</span>
      )}
    </motion.button>
  );
};
