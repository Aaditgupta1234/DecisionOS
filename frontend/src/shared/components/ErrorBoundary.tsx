import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertOctagon, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('DecisionOS Error Boundary caught:', error, errorInfo);
    this.setState({ errorInfo });
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#05070A] text-white flex items-center justify-center p-6" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#05070A', color: '#FFFFFF', padding: '24px' }}>
          <div style={{ maxWidth: '520px', width: '100%', background: '#0B0E14', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '12px', padding: '32px', textAlign: 'center', boxShadow: '0 20px 40px rgba(0,0,0,0.8)' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <AlertOctagon size={28} color="#EF4444" />
            </div>
            
            <h2 style={{ fontSize: '20px', fontWeight: 800, marginBottom: '8px', color: '#FFFFFF' }}>
              Application Render Error
            </h2>
            
            <p style={{ fontSize: '13px', color: '#94A3B8', lineHeight: 1.5, marginBottom: '20px' }}>
              DecisionOS encountered an unexpected runtime error. Your session data remains safe.
            </p>

            {this.state.error && (
              <div style={{ background: '#05070A', border: '1px solid #1E293B', borderRadius: '8px', padding: '12px', fontSize: '11px', color: '#F87171', fontFamily: 'monospace', textAlign: 'left', marginBottom: '24px', overflowX: 'auto', maxHeight: '120px' }}>
                {this.state.error.toString()}
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button
                onClick={this.handleReset}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#1D4ED8', border: '1px solid #3B82F6', color: '#FFFFFF', padding: '9px 18px', borderRadius: '6px', fontSize: '12.5px', fontWeight: 700, cursor: 'pointer' }}
              >
                <RefreshCw size={14} />
                <span>Reload Application</span>
              </button>

              <a
                href="/"
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#131822', border: '1px solid #232B3B', color: '#CBD5E1', padding: '9px 18px', borderRadius: '6px', fontSize: '12.5px', fontWeight: 600, textDecoration: 'none' }}
              >
                <Home size={14} />
                <span>Return to Home</span>
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
