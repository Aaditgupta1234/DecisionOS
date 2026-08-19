import React from 'react';
import { Lock } from 'lucide-react';
import { Link } from 'react-router-dom';

interface PermissionDeniedStateProps {
  requiredRole?: string;
  requiredPermission?: string;
}

export const PermissionDeniedState: React.FC<PermissionDeniedStateProps> = ({
  requiredRole = 'ADMIN / EXECUTIVE',
  requiredPermission,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: '60px 24px',
        background: '#090D14',
        border: '1px solid #1E293B',
        borderRadius: '16px',
        gap: '14px',
      }}
    >
      <div
        style={{
          padding: '16px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: '50%',
        }}
      >
        <Lock size={36} color="#EF4444" />
      </div>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
        Access Restricted by Enterprise Governance Policy
      </h2>
      <p style={{ fontSize: '0.84rem', color: '#94A3B8', maxWidth: '460px', margin: 0 }}>
        Your active role does not possess the required permissions{' '}
        {requiredPermission ? `(${requiredPermission})` : `(${requiredRole})`} to access this executive module.
      </p>
      <Link
        to="/enterprise"
        style={{
          marginTop: '10px',
          padding: '8px 18px',
          background: '#38BDF8',
          color: '#090D14',
          borderRadius: '8px',
          fontWeight: 800,
          fontSize: '0.82rem',
          textDecoration: 'none',
        }}
      >
        Return to Enterprise Command
      </Link>
    </div>
  );
};
