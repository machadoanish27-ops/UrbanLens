import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Compass } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('UrbanLens UI caught error in component tree:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="max-w-2xl mx-auto my-12 p-8 rounded-3xl glass-panel border border-rose-500/30 text-center space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-rose-500/10 text-rose-400 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white">Something went wrong</h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            An unexpected error occurred while rendering this urban intelligence view. You can reload this view or return to the main dashboard.
          </p>
          {this.state.error?.message && (
            <pre className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] text-rose-300 font-mono overflow-x-auto text-left max-w-lg mx-auto">
              {this.state.error.message}
            </pre>
          )}
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={this.handleReset}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Try Again</span>
            </button>
            <a
              href="/"
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Compass className="w-3.5 h-3.5" />
              <span>Return Home</span>
            </a>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
