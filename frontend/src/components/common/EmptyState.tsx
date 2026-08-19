import React from 'react';
import { Layers } from 'lucide-react';
import { Button } from '../../design-system/Button';

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon = <Layers size={32} color="#64748B" />,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '48px 24px',
        background: '#090D14',
        border: '1px solid #1E293B',
        borderRadius: '14px',
        gap: '12px',
      }}
    >
      <div style={{ padding: '12px', background: 'rgba(15, 23, 42, 0.6)', borderRadius: '12px' }}>
        {icon}
      </div>
      <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>{title}</h3>
      <p style={{ fontSize: '0.8rem', color: '#64748B', maxWidth: '420px', margin: 0 }}>
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="secondary" size="sm" onClick={onAction} style={{ marginTop: '8px' }}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
