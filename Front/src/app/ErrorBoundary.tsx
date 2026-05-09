import { Component, type ErrorInfo, type ReactNode } from 'react'
import { reportError } from '../utils/reportError'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    void reportError({
      kind: 'react_error_boundary',
      message: error.message,
      stack: error.stack,
      component_stack: errorInfo.componentStack,
    })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="app-shell min-h-screen flex items-center justify-center p-6">
          <div className="app-panel max-w-md border-2 border-neon-pink p-5 text-center shadow-[0_0_18px_rgba(255,0,85,0.35)]">
            <div className="pixel-font text-sm text-neon-pink">SYSTEM FAILURE</div>
            <div className="app-muted mt-3 arcade-font text-[10px]">
              O front capturou um erro inesperado e registrou os detalhes para desenvolvimento.
            </div>
            <button
              type="button"
              className="mt-4 border-2 border-neon-pink px-4 py-2 arcade-font text-[10px] text-neon-pink"
              onClick={() => window.location.reload()}
            >
              RECARREGAR
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
