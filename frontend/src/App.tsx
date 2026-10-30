import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from './components/ErrorBoundary';
import { OriginDestinationProvider } from './context/OriginDestinationContext';
import { UrbanProvider } from './context/UrbanContext';
import { AppLayout } from './layouts/AppLayout';

// Public Views
const LandingPage = lazy(() => import('./views/LandingPage').then((m) => ({ default: m.LandingPage })));
const AuthLogin = lazy(() => import('./views/AuthLogin').then((m) => ({ default: m.AuthLogin })));
const AuthSignUp = lazy(() => import('./views/AuthSignUp').then((m) => ({ default: m.AuthSignUp })));
const AuthForgotPassword = lazy(() => import('./views/AuthForgotPassword').then((m) => ({ default: m.AuthForgotPassword })));
const CityOnboarding = lazy(() => import('./views/CityOnboarding').then((m) => ({ default: m.CityOnboarding })));

// Application Shell Views
const DashboardOverview = lazy(() => import('./views/DashboardOverview').then((m) => ({ default: m.DashboardOverview })));
const CityExplorerPage = lazy(() => import('./views/CityExplorerPage').then((m) => ({ default: m.CityExplorerPage })));
const CityDetailPage = lazy(() => import('./views/CityDetailPage').then((m) => ({ default: m.CityDetailPage })));
const SpatialIntelligencePage = lazy(() => import('./views/SpatialIntelligencePage').then((m) => ({ default: m.SpatialIntelligencePage })));
const AiIntelligencePage = lazy(() => import('./views/AiIntelligencePage').then((m) => ({ default: m.AiIntelligencePage })));
const CompareCitiesPage = lazy(() => import('./views/CompareCitiesPage').then((m) => ({ default: m.CompareCitiesPage })));
const EnvironmentPage = lazy(() => import('./views/EnvironmentPage').then((m) => ({ default: m.EnvironmentPage })));
const CostOfLivingPage = lazy(() => import('./views/CostOfLivingPage').then((m) => ({ default: m.CostOfLivingPage })));
const EducationPage = lazy(() => import('./views/EducationPage').then((m) => ({ default: m.EducationPage })));
const UniversitiesPage = lazy(() => import('./views/UniversitiesPage').then((m) => ({ default: m.UniversitiesPage })));
const LivePulsePage = lazy(() => import('./views/LivePulsePage').then((m) => ({ default: m.LivePulsePage })));
const AnalyticsPage = lazy(() => import('./views/AnalyticsPage').then((m) => ({ default: m.AnalyticsPage })));
const PredictionsPage = lazy(() => import('./views/PredictionsPage').then((m) => ({ default: m.PredictionsPage })));
const PsoOptimizationPage = lazy(() => import('./views/PsoOptimizationPage').then((m) => ({ default: m.PsoOptimizationPage })));
const QuantumQpuPage = lazy(() => import('./views/QuantumQpuPage').then((m) => ({ default: m.QuantumQpuPage })));
const AlertsPage = lazy(() => import('./views/AlertsPage').then((m) => ({ default: m.AlertsPage })));
const ReportsPage = lazy(() => import('./views/ReportsPage').then((m) => ({ default: m.ReportsPage })));
const SettingsPage = lazy(() => import('./views/SettingsPage').then((m) => ({ default: m.SettingsPage })));
const ProfilePage = lazy(() => import('./views/ProfilePage').then((m) => ({ default: m.ProfilePage })));
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
      <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
      <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wider uppercase">SYNCHRONIZING TELEMETRY...</span>
    </div>
  );
}

// Helper to redirect legacy /city/:cityId to /app/city/:cityId
function LegacyCityRedirect() {
  const { cityId } = useParams();
  return <Navigate to={`/app/city/${cityId || 'city_1356226629'}`} replace />;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <OriginDestinationProvider>
          <BrowserRouter>
            <UrbanProvider>
              <Routes>
                {/* Public Landing & Auth Routes */}
                <Route
                  path="/"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <LandingPage />
                    </Suspense>
                  }
                />
                <Route
                  path="/login"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <AuthLogin />
                    </Suspense>
                  }
                />
                <Route
                  path="/signup"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <AuthSignUp />
                    </Suspense>
                  }
                />
                <Route
                  path="/forgot-password"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <AuthForgotPassword />
                    </Suspense>
                  }
                />

                {/* UrbanLens Application Shell */}
                <Route path="/app" element={<AppLayout />}>
                  <Route
                    index
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <DashboardOverview />
                      </Suspense>
                    }
                  />
                  <Route
                    path="explore"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <CityExplorerPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="city/:cityId"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <CityDetailPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="map"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <SpatialIntelligencePage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="ask"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <AiIntelligencePage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="compare"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <CompareCitiesPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="environment"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <EnvironmentPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="weather"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <EnvironmentPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="air-quality"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <EnvironmentPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="cost"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <CostOfLivingPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="education"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <EducationPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="universities"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <UniversitiesPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="pulse"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <LivePulsePage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="analytics"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <AnalyticsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="predictions"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <PredictionsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="optimization"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <PsoOptimizationPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="quantum"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <QuantumQpuPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="alerts"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <AlertsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="reports"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <ReportsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="settings"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <SettingsPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="profile"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <ProfilePage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="onboarding"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <CityOnboarding />
                      </Suspense>
                    }
                  />
                  <Route
                    path="saved"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <CityExplorerPage />
                      </Suspense>
                    }
                  />
                  <Route
                    path="workspace"
                    element={
                      <Suspense fallback={<PageLoader />}>
                        <ReportsPage />
                      </Suspense>
                    }
                  />
                </Route>

                {/* Legacy Backward-Compatible Redirects */}
                <Route path="/city/:cityId" element={<LegacyCityRedirect />} />
                <Route path="/cities" element={<Navigate to="/app/explore" replace />} />
                <Route path="/compare" element={<Navigate to="/app/compare" replace />} />
                <Route path="/ask" element={<Navigate to="/app/ask" replace />} />
                <Route path="/dashboard" element={<Navigate to="/app" replace />} />

                {/* 404 Catch-All */}
                <Route
                  path="*"
                  element={
                    <Suspense fallback={<PageLoader />}>
                      <NotFoundPage />
                    </Suspense>
                  }
                />
              </Routes>
            </UrbanProvider>
          </BrowserRouter>
        </OriginDestinationProvider>
      </ErrorBoundary>
    </QueryClientProvider>
  );
}

export default App;
