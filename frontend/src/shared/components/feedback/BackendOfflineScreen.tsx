import React from 'react';
import { ServerOff, RefreshCw, Terminal, ArrowLeft } from 'lucide-react';

interface Props {
  onRetry: () => void;
  isRetrying?: boolean;
}

export const BackendOfflineScreen: React.FC<Props> = ({ onRetry, isRetrying = false }) => {
  return (
    <div
      style={{
        minHeight: '80vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        color: '#FFFFFF',
      }}
    >
      <div
        style={{
          maxWidth: '560px',
          width: '100%',
          background: '#090C12',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: '14px',
          padding: '36px',
          textAlign: 'center',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.85)',
        }}
      >
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.35)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            boxShadow: '0 0 20px rgba(239, 68, 68, 0.2)',
          }}
        >
          <ServerOff size={30} color="#EF4444" />
        </div>

        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            padding: '3px 10px',
            borderRadius: '20px',
            fontSize: '11px',
            fontWeight: 700,
            color: '#F87171',
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            marginBottom: '12px',
          }}
        >
          <span>● Backend Offline</span>
        </div>

        <h2 style={{ fontSize: '22px', fontWeight: 800, marginBottom: '10px', letterSpacing: '-0.02em' }}>
          DecisionOS Gateway Offline
        </h2>

        <p style={{ fontSize: '13.5px', color: '#94A3B8', lineHeight: 1.6, marginBottom: '24px' }}>
          Unable to establish a secure handshake with the DecisionOS FastAPI backend on{' '}
          <code style={{ color: '#F1F5F9', background: '#171D27', padding: '2px 6px', borderRadius: '4px', fontSize: '12px' }}>
            localhost:8000
          </code>.
        </p>

        <div
          style={{
            background: '#04060A',
            border: '1px solid #1A2230',
            borderRadius: '8px',
            padding: '14px 16px',
            textAlign: 'left',
            marginBottom: '28px',
            fontSize: '12px',
            fontFamily: 'monospace',
            color: '#CBD5E1',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#64748B', fontSize: '11px', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 700 }}>
            <Terminal size={12} />
            <span>Start Backend Service</span>
          </div>
          <div style={{ color: '#38BDF8', fontWeight: 600 }}>
            cd backend && uvicorn app.main:app --reload --port 8000
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
          <button
            type="button"
            onClick={onRetry}
            disabled={isRetrying}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: '#1D4ED8',
              border: '1px solid #3B82F6',
              color: '#FFFFFF',
              padding: '10px 22px',
              borderRadius: '7px',
              fontSize: '13px',
              fontWeight: 700,
              cursor: isRetrying ? 'not-allowed' : 'pointer',
              opacity: isRetrying ? 0.7 : 1,
              transition: 'all 0.15s ease',
            }}
          >
            <RefreshCw size={14} style={{ animation: isRetrying ? 'spin 1s linear infinite' : 'none' }} />
            <span>{isRetrying ? 'Checking Connection...' : 'Retry Connection'}</span>
          </button>

          <a
            href="/"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: '#111620',
              border: '1px solid #20293A',
              color: '#94A3B8',
              padding: '10px 18px',
              borderRadius: '7px',
              fontSize: '13px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            <ArrowLeft size={14} />
            <span>Return Home</span>
          </a>
        </div>
      </div>
    </div>
  );
};
