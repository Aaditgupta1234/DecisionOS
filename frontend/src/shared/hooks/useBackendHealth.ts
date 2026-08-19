import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

export interface HealthState {
  status: 'connected' | 'offline' | 'checking';
  latencyMs: number | null;
  version?: string;
  environment?: string;
  lastChecked: Date | null;
}

export function useBackendHealth(pollIntervalMs: number = 20000) {
  const [health, setHealth] = useState<HealthState>({
    status: 'checking',
    latencyMs: null,
    lastChecked: null,
  });

  const checkHealth = useCallback(async () => {
    const startTime = performance.now();
    try {
      // First try /api/v1/health, then fallback to /health
      const response = await axios.get('/api/v1/health', { timeout: 4000 });
      const latency = Math.round(performance.now() - startTime);
      setHealth({
        status: 'connected',
        latencyMs: latency,
        version: response.data?.version || '1.0.0',
        environment: response.data?.environment || 'development',
        lastChecked: new Date(),
      });
    } catch {
      try {
        const fallbackRes = await axios.get('/health', { timeout: 3000 });
        const latency = Math.round(performance.now() - startTime);
        setHealth({
          status: 'connected',
          latencyMs: latency,
          version: fallbackRes.data?.version || '1.0.0',
          environment: fallbackRes.data?.environment || 'development',
          lastChecked: new Date(),
        });
      } catch {
        setHealth({
          status: 'offline',
          latencyMs: null,
          lastChecked: new Date(),
        });
      }
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [checkHealth, pollIntervalMs]);

  return { ...health, checkHealth };
}
