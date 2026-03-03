/**
 * Root component with React Router configuration.
 *
 * Routes (per frontend-contract.md §1)
 * --------------------------------------
 * /                      → Dashboard (landing page)
 * /chat                  → ChatView (new conversation)
 * /chat/:conversationId  → ChatView (existing conversation)
 * /documents             → DocumentList
 * /documents/:documentId → DocumentDetail
 * /settings              → Settings
 */
import { ErrorBoundary, type FallbackProps } from 'react-error-boundary';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/common/Layout';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';

// Lazy-loaded pages (will be created in later phases)
import { lazy, Suspense } from 'react';
import LoadingSpinner from './components/common/LoadingSpinner';

// Placeholder pages until their Phase implementations
const ChatView = lazy(() => import('./pages/ChatView'));
const DocumentList = lazy(() => import('./pages/DocumentList'));
const DocumentDetail = lazy(() => import('./pages/DocumentDetail'));

function ErrorFallback({ error }: FallbackProps) {
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div className="error-boundary">
      <h2>Something went wrong</h2>
      <p>{message}</p>
      <button
        onClick={() => window.location.reload()}
        type="button"
      >
        Reload page
      </button>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route
              path="chat"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <ChatView />
                </Suspense>
              }
            />
            <Route
              path="chat/:conversationId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <ChatView />
                </Suspense>
              }
            />
            <Route
              path="documents"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <DocumentList />
                </Suspense>
              }
            />
            <Route
              path="documents/:documentId"
              element={
                <Suspense fallback={<LoadingSpinner />}>
                  <DocumentDetail />
                </Suspense>
              }
            />
            <Route path="settings" element={<Settings />} />
            {/* Catch-all redirect to dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
