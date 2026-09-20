import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
  sectionKey?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class EnterpriseCardErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`[EnterpriseCardErrorBoundary:${this.props.sectionKey || 'Card'}]`, error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.06)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '12px',
            padding: '20px 24px',
            margin: '8px 0',
            color: '#F87171',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <AlertTriangle size={18} color="#EF4444" />
              </div>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#FEE2E2' }}>
                  {this.props.fallbackTitle || 'Enterprise Intelligence Service Error'}
                </div>
                <div style={{ fontSize: '11px', color: '#FCA5A5' }}>
                  This telemetry component encountered a rendering issue. Other workspace services remain active.
                </div>
              </div>
            </div>

            <button
              onClick={this.handleRetry}
              style={{
                background: 'rgba(239, 68, 68, 0.20)',
                border: '1px solid rgba(239, 68, 68, 0.40)',
                color: '#FFFFFF',
                padding: '6px 14px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
            >
              <RefreshCw size={12} />
              <span>Retry Component</span>
            </button>
          </div>

          {this.state.error && (
            <div
              style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '8px 12px',
                borderRadius: '6px',
                fontSize: '11px',
                fontFamily: 'monospace',
                color: '#FECACA',
                overflowX: 'auto',
              }}
            >
              {this.state.error.message || this.state.error.toString()}
            </div>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
