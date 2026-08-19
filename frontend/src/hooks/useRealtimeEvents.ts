import { useState, useEffect } from 'react';
import { EnterpriseEvent } from '../events/EnterpriseEvent';

export const useRealtimeEvents = (onEventReceived?: (event: EnterpriseEvent) => void) => {
  const [events, setEvents] = useState<EnterpriseEvent[]>([]);

  useEffect(() => {
    // Simulated periodic enterprise event stream
    const interval = setInterval(() => {
      const sampleEvents: EnterpriseEvent[] = [
        {
          id: `evt-${Date.now()}`,
          type: 'DECISION_APPROVED',
          source: 'GovernanceComplianceEngine',
          timestamp: new Date().toISOString(),
          payload: { decisionCode: 'DEC-2026-042', valueArr: 340000 },
        },
        {
          id: `evt-${Date.now() + 1}`,
          type: 'PLAYBOOK_EXECUTED',
          source: 'AutonomousPlaybookEngine',
          timestamp: new Date().toISOString(),
          payload: { playbookCode: 'PBT-RETENTION-RECOVERY', costUsd: 0.14 },
        },
      ];

      const chosen = sampleEvents[Math.floor(Math.random() * sampleEvents.length)];
      setEvents((prev) => [chosen, ...prev].slice(0, 20));
      onEventReceived?.(chosen);
    }, 45000);

    return () => clearInterval(interval);
  }, [onEventReceived]);

  return { events };
};
