import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, ShieldCheck, Sparkles, Activity, AlertTriangle } from 'lucide-react';
import { useMotion } from './MotionProvider';
import { MOTION_LIMITS, EASING, DURATIONS } from './motionTokens';

export interface FindingItem {
  id: string;
  title: string;
  category?: string;
  impact?: string;
  severity?: 'critical' | 'high' | 'medium' | 'low';
  confidence?: number;
}

interface IntelligenceRevealProps {
  findings: FindingItem[];
  analyzingLabel?: string;
  rootCausesCount?: number;
  actionsCount?: number;
  onComplete?: () => void;
  renderItem?: (item: FindingItem, index: number) => React.ReactNode;
}

export const IntelligenceReveal: React.FC<IntelligenceRevealProps> = ({
  findings,
  analyzingLabel = 'Isolating root cause causality...',
  rootCausesCount,
  actionsCount,
  onComplete,
  renderItem,
}) => {
  const { shouldReduceMotion } = useMotion();
  const [revealedCount, setRevealedCount] = useState<number>(shouldReduceMotion ? findings.length : 0);
  const [isInvestigationComplete, setIsInvestigationComplete] = useState<boolean>(shouldReduceMotion);

  // Stagger cap: animate at most first 10 items sequentially, the rest resolve together
  const animatedBatchLimit = Math.min(findings.length, MOTION_LIMITS.maxStaggerBatchSize);

  useEffect(() => {
    if (shouldReduceMotion) {
      setRevealedCount(findings.length);
      setIsInvestigationComplete(true);
      if (onComplete) onComplete();
      return;
    }

    setRevealedCount(0);
    setIsInvestigationComplete(false);

    let current = 0;
    const interval = setInterval(() => {
      current += 1;
      if (current <= animatedBatchLimit) {
        setRevealedCount(current);
      } else {
        // Resolve all remaining items at once
        setRevealedCount(findings.length);
        setIsInvestigationComplete(true);
        clearInterval(interval);
        if (onComplete) onComplete();
      }
    }, MOTION_LIMITS.intelligenceRevealDelayMs);

    return () => clearInterval(interval);
  }, [findings.length, shouldReduceMotion, animatedBatchLimit, onComplete]);

  return (
    <div className="intelligence-reveal-container" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {/* 1. Active Scanning Banner (while investigating) */}
      <AnimatePresence>
        {!isInvestigationComplete && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: DURATIONS.fast, ease: EASING.executive }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 12px',
              background: 'rgba(56, 189, 248, 0.08)',
              border: '1px solid rgba(56, 189, 248, 0.25)',
              borderRadius: '8px',
              fontSize: '0.78rem',
              color: '#38BDF8',
              fontWeight: 600,
              alignSelf: 'flex-start',
            }}
          >
            <Activity size={13} className="animate-spin" style={{ animationDuration: '3s' }} />
            <span>{analyzingLabel}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 2. Sequential Findings List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {findings.slice(0, revealedCount).map((finding, idx) => {
          if (renderItem) {
            return (
              <motion.div
                key={finding.id || idx}
                initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: DURATIONS.fast, ease: EASING.executive }}
              >
                {renderItem(finding, idx)}
              </motion.div>
            );
          }

          // Default sleek executive finding row
          const isCritical = finding.severity === 'critical' || finding.severity === 'high';
          return (
            <motion.div
              key={finding.id || idx}
              initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: DURATIONS.fast, ease: EASING.executive }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 14px',
                background: '#090D14',
                border: '1px solid #1A2230',
                borderRadius: '8px',
                transition: 'border-color 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle2 size={15} color={isCritical ? '#EF4444' : '#10B981'} style={{ flexShrink: 0 }} />
                <span style={{ fontSize: '0.84rem', fontWeight: 600, color: '#E2E8F0' }}>
                  {finding.title}
                </span>
              </div>

              {finding.impact && (
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: isCritical ? '#EF4444' : '#38BDF8',
                    background: isCritical ? 'rgba(239, 68, 68, 0.1)' : 'rgba(56, 189, 248, 0.1)',
                    border: `1px solid ${isCritical ? 'rgba(239, 68, 68, 0.25)' : 'rgba(56, 189, 248, 0.25)'}`,
                    padding: '2px 8px',
                    borderRadius: '4px',
                  }}
                >
                  {finding.impact}
                </span>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* 3. Investigation Complete Terminal State */}
      <AnimatePresence>
        {isInvestigationComplete && (
          <motion.div
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.18, ease: EASING.executive }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 16px',
              background: 'linear-gradient(90deg, rgba(16, 185, 129, 0.08) 0%, rgba(9, 13, 20, 0.95) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '8px',
              marginTop: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={16} color="#10B981" />
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF' }}>
                Investigation Complete
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.74rem', color: '#94A3B8', fontWeight: 600 }}>
              <span>{findings.length} Findings Isolated</span>
              {rootCausesCount !== undefined && (
                <>
                  <span style={{ color: '#334155' }}>•</span>
                  <span>{rootCausesCount} Root Causes Traced</span>
                </>
              )}
              {actionsCount !== undefined && (
                <>
                  <span style={{ color: '#334155' }}>•</span>
                  <span>{actionsCount} Strategic Actions</span>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
