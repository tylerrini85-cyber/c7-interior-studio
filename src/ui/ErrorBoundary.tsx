import { Component, type ReactNode } from 'react';

/** Keeps a renderer failure from blanking the whole app; the project document is unaffected. */
export class ErrorBoundary extends Component<{ children: ReactNode; label?: string }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  componentDidCatch(error: Error) { console.error('[c7] render error', error); }
  render() {
    if (this.state.error) {
      return (
        <div className="loading" role="alert">
          <div className="loading-card">
            <h3>{this.props.label ?? 'The 3D view hit a problem'}</h3>
            <p className="error">{this.state.error.message.slice(0, 200)}</p>
            <p className="muted small">Your project is saved. Reload to continue.</p>
            <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>Reload</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
