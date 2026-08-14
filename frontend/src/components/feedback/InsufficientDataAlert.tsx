import React from 'react';
import { Info } from 'lucide-react';

interface InsufficientDataAlertProps {
  title?: string;
  message: string;
  requirementDetails?: string;
}

export const InsufficientDataAlert: React.FC<InsufficientDataAlertProps> = ({
  title = 'Analytical Data Requirement Not Met',
  message,
  requirementDetails,
}) => {
  return (
    <div
      style={{
        padding: '16px 20px',
        backgroundColor: 'var(--color-info-subtle)',
        border: '1px solid var(--color-info-border)',
        borderRadius: 'var(--radius-md)',
        color: 'var(--text-main)',
        margin: '16px 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <Info size={20} color="var(--color-info)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h4 style={{ color: 'var(--color-info)', fontSize: '0.9rem', marginBottom: '4px' }}>
            {title}
          </h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: requirementDetails ? '8px' : '0' }}>
            {message}
          </p>
          {requirementDetails && (
            <div
              style={{
                fontSize: '0.75rem',
                backgroundColor: 'rgba(6, 182, 212, 0.08)',
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                borderLeft: '2px solid var(--color-info)',
                color: 'var(--text-muted)',
              }}
            >
              {requirementDetails}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
