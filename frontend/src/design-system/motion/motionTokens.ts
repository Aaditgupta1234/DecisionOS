/**
 * DecisionOS Central Motion & Performance Tokens
 * Executive-grade easing curves, strict scaling bounds, and performance budgets.
 */

export const PERFORMANCE_BUDGET = {
  targetFPS: 60,
  maxConcurrentAnimations: 12,
  maxAnimationDurationMs: 1000,
  allowedProperties: ['opacity', 'transform'] as const,
};

export const MOTION_LIMITS = {
  cardHoverScale: 1.008,          // 1.005 – 1.01
  buttonHoverScale: 1.015,        // 1.01 – 1.02
  maxAllowedScale: 1.03,          // Absolute hard ceiling anywhere
  intelligenceRevealDelayMs: 65,  // 60ms – 80ms per finding
  healthScoreDurationMs: 850,     // Clamped strictly between 700ms – 1000ms
  maxStaggerBatchSize: 10,        // Max items sequentially animated in any list
};

export const EASING = {
  // Stripe/Linear-style swift entry with silky natural settling
  executive: [0.16, 1, 0.3, 1] as const,
  // Snappy response for buttons, toggles, and micro-interactions
  micro: [0.22, 1, 0.36, 1] as const,
  // Gentle curve for large area opacity fades and dialog backdrops
  gentle: [0.25, 0.1, 0.25, 1] as const,
  // Standard CSS timing strings
  cssExecutive: 'cubic-bezier(0.16, 1, 0.3, 1)',
  cssMicro: 'cubic-bezier(0.22, 1, 0.36, 1)',
};

export const DURATIONS = {
  instant: 0.1,
  fast: 0.16,
  normal: 0.28,
  deliberate: 0.42,
  reveal: 0.65,
  healthScore: 0.85,
};

export const SPRING = {
  snappy: { type: 'spring', stiffness: 420, damping: 32 } as const,
  gentle: { type: 'spring', stiffness: 260, damping: 28 } as const,
  subtleHover: { type: 'spring', stiffness: 500, damping: 35 } as const,
};
