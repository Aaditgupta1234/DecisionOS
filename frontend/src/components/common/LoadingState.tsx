import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  height?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading decision telemetry...',
  height = '300px',
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        height,
        color: '#64748B',
      }}
    >
      <Loader2 size={28} className="animate-spin" color="#38BDF8" />
      <span style={{ fontSize: '0.84rem', fontWeight: 600 }}>{message}</span>
    </div>
  );
};
