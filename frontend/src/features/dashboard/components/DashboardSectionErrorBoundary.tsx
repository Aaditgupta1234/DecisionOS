import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  title: string;
  sectionKey: string;
  children: ReactNode;
  onRetry?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class DashboardSectionErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`[DashboardErrorBoundary:${this.props.sectionKey}]`, error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onRetry) {
      this.props.onRetry();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-slate-900/60 border border-rose-500/30 rounded-2xl p-6 my-4 shadow-xl backdrop-blur-sm">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 shrink-0">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-semibold text-rose-300">
                {this.props.title} Unavailable
              </h3>
              <p className="text-sm text-slate-400 mt-1">
                An isolated rendering error occurred in this intelligence section. The rest of your executive workspace remains active and secure.
              </p>
              {this.state.error && (
                <div className="mt-2 text-xs font-mono text-rose-400/80 bg-rose-950/30 p-2 rounded border border-rose-900/40 truncate">
                  {this.state.error.message}
                </div>
              )}
              <div className="mt-4 flex items-center gap-3">
                <button
                  onClick={this.handleReset}
                  className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 rounded-lg transition-colors"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Retry Section
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
