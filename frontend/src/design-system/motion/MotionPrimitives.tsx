import React from 'react';
import { motion, AnimatePresence, HTMLMotionProps } from 'framer-motion';
import { useMotion } from './MotionProvider';
import { EASING, DURATIONS } from './motionTokens';

interface BaseMotionProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children?: React.ReactNode;
  className?: string;
  delay?: number;
  duration?: number;
}

/**
 * 1. FadeIn: Pure opacity reveal (0 -> 1)
 */
export const FadeIn: React.FC<BaseMotionProps> = ({
  children,
  className,
  delay = 0,
  duration = DURATIONS.normal,
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{
        duration: shouldReduceMotion ? 0.05 : duration,
        delay: shouldReduceMotion ? 0 : delay,
        ease: EASING.gentle,
      }}
      className={className}
      style={style}
      {...props}
    >
      {children}
    </motion.div>
  );
};

/**
 * 2. FadeUp: Subtle translateY reveal (16px -> 0) with opacity
 */
interface FadeUpProps extends BaseMotionProps {
  distance?: number;
  viewportOnce?: boolean;
}

export const FadeUp: React.FC<FadeUpProps> = ({
  children,
  className,
  distance = 16,
  delay = 0,
  duration = DURATIONS.normal,
  viewportOnce = true,
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  const initial = shouldReduceMotion
    ? { opacity: 0 }
    : { opacity: 0, y: distance };

  const target = shouldReduceMotion
    ? { opacity: 1 }
    : { opacity: 1, y: 0 };

  return (
    <motion.div
      initial={initial}
      whileInView={target}
      viewport={{ once: viewportOnce, margin: '-20px' }}
      transition={{
        duration: shouldReduceMotion ? 0.05 : duration,
        delay: shouldReduceMotion ? 0 : delay,
        ease: EASING.executive,
      }}
      className={className}
      style={style}
      {...props}
    >
      {children}
    </motion.div>
  );
};

/**
 * 3. FadeDown: Subtle -16px translateY downward reveal
 */
export const FadeDown: React.FC<FadeUpProps> = ({
  children,
  className,
  distance = 16,
  delay = 0,
  duration = DURATIONS.normal,
  viewportOnce = true,
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  const initial = shouldReduceMotion
    ? { opacity: 0 }
    : { opacity: 0, y: -distance };

  const target = shouldReduceMotion
    ? { opacity: 1 }
    : { opacity: 1, y: 0 };

  return (
    <motion.div
      initial={initial}
      whileInView={target}
      viewport={{ once: viewportOnce, margin: '-20px' }}
      transition={{
        duration: shouldReduceMotion ? 0.05 : duration,
        delay: shouldReduceMotion ? 0 : delay,
        ease: EASING.executive,
      }}
      className={className}
      style={style}
      {...props}
    >
      {children}
    </motion.div>
  );
};

/**
 * 4. StaggerContainer: Orchestrates rapid sequential child reveals
 */
interface StaggerContainerProps extends BaseMotionProps {
  staggerDelay?: number;
  delayChildren?: number;
  viewportOnce?: boolean;
}

export const StaggerContainer: React.FC<StaggerContainerProps> = ({
  children,
  className,
  staggerDelay = 0.05,
  delayChildren = 0,
  viewportOnce = true,
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  const containerVariants = {
    hidden: { opacity: shouldReduceMotion ? 1 : 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: shouldReduceMotion ? 0 : staggerDelay,
        delayChildren: shouldReduceMotion ? 0 : delayChildren,
      },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="show"
      viewport={{ once: viewportOnce, margin: '-20px' }}
      className={className}
      style={style}
      {...props}
    >
      {children}
    </motion.div>
  );
};

/**
 * 5. StaggerItem: Child component conforming to StaggerContainer
 */
export const StaggerItem: React.FC<BaseMotionProps> = ({
  children,
  className,
  style,
  ...props
}) => {
  const { shouldReduceMotion } = useMotion();

  const itemVariants = {
    hidden: shouldReduceMotion
      ? { opacity: 0 }
      : { opacity: 0, y: 12 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        duration: shouldReduceMotion ? 0.05 : DURATIONS.fast,
        ease: EASING.executive,
      },
    },
  };

  return (
    <motion.div variants={itemVariants} className={className} style={style} {...props}>
      {children}
    </motion.div>
  );
};

/**
 * 6. PageTransition: Fast desktop-first route crossfade with micro-translate
 */
export const PageTransition: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className,
}) => {
  const { shouldReduceMotion } = useMotion();

  return (
    <motion.div
      initial={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={shouldReduceMotion ? { opacity: 0 } : { opacity: 0, y: -4 }}
      transition={{
        duration: DURATIONS.fast,
        ease: EASING.executive,
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

/**
 * 7. CrossFade: Used for data refreshes and state changes without layout shift
 */
export const CrossFade: React.FC<{
  children: React.ReactNode;
  stateKey: string | number;
  className?: string;
}> = ({ children, stateKey, className }) => {
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={stateKey}
        initial={{ opacity: 0.85 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0.85 }}
        transition={{ duration: DURATIONS.fast, ease: EASING.gentle }}
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};
