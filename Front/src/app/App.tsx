import { Suspense, useEffect } from 'react';
import { RouterProvider } from 'react-router';
import { ErrorBoundary } from './ErrorBoundary';
import { router } from './routes';
import { reportError } from '../utils/reportError';

function PageFallback() {
  return (
    <div className="app-shell min-h-screen flex items-center justify-center">
      <div className="pixel-font text-neon-green text-xs animate-pulse">LOADING...</div>
    </div>
  );
}

export default function App() {
  useEffect(() => {
    const onError = (event: ErrorEvent) => {
      void reportError({
        kind: 'window_error',
        message: event.message || 'Unhandled window error',
        stack: event.error?.stack ?? null,
        extra: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
        },
      })
    }

    const onUnhandledRejection = (event: PromiseRejectionEvent) => {
      const reason = event.reason
      void reportError({
        kind: 'unhandled_rejection',
        message: reason instanceof Error ? reason.message : String(reason),
        stack: reason instanceof Error ? reason.stack : null,
      })
    }

    window.addEventListener('error', onError)
    window.addEventListener('unhandledrejection', onUnhandledRejection)
    return () => {
      window.removeEventListener('error', onError)
      window.removeEventListener('unhandledrejection', onUnhandledRejection)
    }
  }, [])

  return (
    <ErrorBoundary>
      <Suspense fallback={<PageFallback />}>
        <RouterProvider router={router} />
      </Suspense>
    </ErrorBoundary>
  );
}
