import React, { createContext, useContext, useEffect, useState, useMemo } from 'react';
import { MOTION_LIMITS } from './motionTokens';

interface MotionContextValue {
  /** True when the OS prefers reduced motion */
  shouldReduceMotion: boolean;
  /** True when the document tab is backgrounded/hidden to suspend animations */
  isSuspended: boolean;
  /** Maximum items allowed to sequentially animate in a single list */
  maxBatchSize: number;
}

const MotionContext = createContext<MotionContextValue>({
  shouldReduceMotion: false,
  isSuspended: false,
  maxBatchSize: MOTION_LIMITS.maxStaggerBatchSize,
});

export const useMotion = () => useContext(MotionContext);

interface MotionProviderProps {
  children: React.ReactNode;
  overrideReduceMotion?: boolean;
}

export const MotionProvider: React.FC<MotionProviderProps> = ({
  children,
  overrideReduceMotion,
}) => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);
  const [isSuspended, setIsSuspended] = useState<boolean>(false);

  // 1. Reduced Motion Detection
  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    try {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      if (!mediaQuery) return;
      setPrefersReducedMotion(mediaQuery.matches);

      const handleChange = (event: MediaQueryListEvent) => {
        setPrefersReducedMotion(event.matches);
      };

      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
      } else if ((mediaQuery as any).addListener) {
        (mediaQuery as any).addListener(handleChange);
        return () => (mediaQuery as any).removeListener(handleChange);
      }
    } catch {
      // Safe fallback in non-browser environments
    }
  }, []);

  // 2. Visibility Suspension (Pauses animations on background tab to save CPU & battery)
  useEffect(() => {
    if (typeof document === 'undefined') return;

    const handleVisibilityChange = () => {
      setIsSuspended(document.visibilityState === 'hidden');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const value = useMemo<MotionContextValue>(
    () => ({
      shouldReduceMotion: overrideReduceMotion ?? prefersReducedMotion,
      isSuspended,
      maxBatchSize: MOTION_LIMITS.maxStaggerBatchSize,
    }),
    [overrideReduceMotion, prefersReducedMotion, isSuspended]
  );

  return <MotionContext.Provider value={value}>{children}</MotionContext.Provider>;
};
