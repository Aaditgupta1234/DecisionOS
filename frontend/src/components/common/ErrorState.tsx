import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';
import { Button } from '../../design-system/Button';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Failed to load intelligence telemetry',
  message = 'An unexpected network or engine error occurred. Please retry your request.',
  onRetry,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '40px 20px',
        background: 'rgba(239, 68, 68, 0.05)',
        border: '1px solid rgba(239, 68, 68, 0.2)',
        borderRadius: '14px',
        gap: '12px',
      }}
    >
      <AlertTriangle size={32} color="#EF4444" />
      <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>{title}</h3>
      <p style={{ fontSize: '0.8rem', color: '#94A3B8', maxWidth: '420px', margin: 0 }}>{message}</p>
      {onRetry && (
        <Button variant="danger" size="sm" icon={<RotateCcw size={14} />} onClick={onRetry}>
          Retry Query
        </Button>
      )}
    </div>
  );
};
