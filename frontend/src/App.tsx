import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RootLayout } from './layouts/RootLayout';
import { ErrorBoundary } from './components/ErrorBoundary';
import { OriginDestinationProvider } from './context/OriginDestinationContext';
import { OriginSelectorModal } from './components/OriginSelectorModal';

const HomePage = lazy(() => import('./pages/HomePage').then((m) => ({ default: m.HomePage })));
const CityPage = lazy(() => import('./pages/CityPage').then((m) => ({ default: m.CityPage })));
const AskPage = lazy(() => import('./pages/AskPage').then((m) => ({ default: m.AskPage })));
const ComparePage = lazy(() => import('./pages/ComparePage').then((m) => ({ default: m.ComparePage })));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 2 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function PageLoader() {
  return (
    <div className="w-full min-h-[50vh] flex flex-col items-center justify-center space-y-3">
      <div className="w-8 h-8 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
      <span className="text-xs text-slate-400 font-medium">Loading urban intelligence...</span>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <OriginDestinationProvider>
          <BrowserRouter>
            <OriginSelectorModal />
            <Routes>
              <Route path="/" element={<RootLayout />}>
                <Route
                  index
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <HomePage />
                    </Suspense>
                  }
                />
                <Route
                  path="city/:cityId"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <CityPage />
                    </Suspense>
                  }
                />
                <Route
                  path="ask"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <AskPage />
                    </Suspense>
                  }
                />
                <Route
                  path="compare"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <ComparePage />
                    </Suspense>
                  }
                />
                <Route
                  path="*"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <NotFoundPage />
                    </Suspense>
                  }
                />
              </Route>
            </Routes>
          </BrowserRouter>
        </OriginDestinationProvider>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}

export default App;
