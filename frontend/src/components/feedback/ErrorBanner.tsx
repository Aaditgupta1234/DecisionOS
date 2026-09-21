import React from 'react';
import { AlertCircle } from 'lucide-react';

interface ErrorBannerProps {
  message?: any;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => {
  let displayMessage = "Intelligence Service Temporarily Unavailable";
  if (typeof message === "string" && message.trim() !== "" && message !== "[object Object]") {
    displayMessage = message;
  } else if (message && typeof message === "object") {
    const extracted =
      message?.response?.data?.message ||
      message?.response?.data?.detail ||
      message?.message;
    if (typeof extracted === "string" && extracted.trim() !== "" && extracted !== "[object Object]") {
      displayMessage = extracted;
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 18px',
        backgroundColor: 'var(--color-danger-subtle)',
        border: '1px solid var(--color-danger-border)',
        borderRadius: 'var(--radius-md)',
        color: 'var(--color-danger)',
        margin: '16px 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <AlertCircle size={18} />
        <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>{displayMessage}</span>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-secondary btn-sm"
          style={{ borderColor: 'var(--color-danger-border)', color: '#fff' }}
        >
          Retry
        </button>
      )}
    </div>
  );
};
