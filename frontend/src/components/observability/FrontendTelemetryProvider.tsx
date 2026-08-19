import React, { createContext, useContext, useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

export interface FrontendErrorEvent {
  id: string;
  message: string;
  source: string;
  timestamp: string;
  route: string;
}

export interface FeatureUsageEvent {
  featureName: string;
  timestamp: string;
  route: string;
}

interface TelemetryContextType {
  errors: FrontendErrorEvent[];
  usageEvents: FeatureUsageEvent[];
  logError: (message: string, source?: string) => void;
  trackFeature: (featureName: string) => void;
}

const TelemetryContext = createContext<TelemetryContextType>({
  errors: [],
  usageEvents: [],
  logError: () => {},
  trackFeature: () => {},
});

export const useFrontendTelemetry = () => useContext(TelemetryContext);

export const FrontendTelemetryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const [errors, setErrors] = useState<FrontendErrorEvent[]>([]);
  const [usageEvents, setUsageEvents] = useState<FeatureUsageEvent[]>([]);

  // Route Performance Logging
  useEffect(() => {
    const startTime = performance.now();
    const currentRoute = location.pathname;

    return () => {
      const durationMs = Math.round(performance.now() - startTime);
      if (durationMs > 20) {
        // Track load
      }
    };
  }, [location]);

  const logError = (message: string, source = 'UI') => {
    const newErr: FrontendErrorEvent = {
      id: `err-${Date.now()}`,
      message,
      source,
      timestamp: new Date().toISOString(),
      route: location.pathname,
    };
    setErrors((prev) => [newErr, ...prev].slice(0, 50));
  };

  const trackFeature = (featureName: string) => {
    const evt: FeatureUsageEvent = {
      featureName,
      timestamp: new Date().toISOString(),
      route: location.pathname,
    };
    setUsageEvents((prev) => [evt, ...prev].slice(0, 100));
  };

  return (
    <TelemetryContext.Provider value={{ errors, usageEvents, logError, trackFeature }}>
      {children}
    </TelemetryContext.Provider>
  );
};
