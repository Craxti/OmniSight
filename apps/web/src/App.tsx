import { lazy, Suspense, type ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/context/AuthContext'
import { I18nProvider } from '@/context/I18nContext'
import { ThemeProvider } from '@/context/ThemeContext'
import { ToastProvider } from '@/context/ToastContext'
import Layout from '@/components/Layout'
import ProtectedRoute from '@/components/ProtectedRoute'
import PageLoader from '@/components/PageLoader'

const LoginPage = lazy(() => import('@/features/auth/LoginPage'))
const ChangePasswordPage = lazy(() => import('@/features/auth/ChangePasswordPage'))
const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage'))
const InventoryPage = lazy(() => import('@/features/inventory/InventoryPage'))
const CIDetailPage = lazy(() => import('@/features/inventory/CIDetailPage'))
const RelationsPage = lazy(() => import('@/features/relations/RelationsPage'))
const GraphPage = lazy(() => import('@/features/graph/GraphPage'))
const CorrelationPage = lazy(() => import('@/features/correlation/CorrelationPage'))
const AuditPage = lazy(() => import('@/features/audit/AuditPage'))
const SettingsPage = lazy(() => import('@/features/settings/SettingsPage'))

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
})

function LazyPage({ children }: { children: ReactNode }) {
  return <Suspense fallback={<PageLoader />}>{children}</Suspense>
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <ThemeProvider>
        <I18nProvider>
          <AuthProvider>
            <ToastProvider>
              <BrowserRouter>
                <Routes>
                  <Route
                    path="/login"
                    element={
                      <LazyPage>
                        <LoginPage />
                      </LazyPage>
                    }
                  />
                  <Route element={<ProtectedRoute />}>
                    <Route
                      path="change-password"
                      element={
                        <LazyPage>
                          <ChangePasswordPage />
                        </LazyPage>
                      }
                    />
                    <Route element={<Layout />}>
                      <Route
                        index
                        element={
                          <LazyPage>
                            <DashboardPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="inventory"
                        element={
                          <LazyPage>
                            <InventoryPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="inventory/:id"
                        element={
                          <LazyPage>
                            <CIDetailPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="relations"
                        element={
                          <LazyPage>
                            <RelationsPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="graph"
                        element={
                          <LazyPage>
                            <GraphPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="correlation"
                        element={
                          <LazyPage>
                            <CorrelationPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="audit"
                        element={
                          <LazyPage>
                            <AuditPage />
                          </LazyPage>
                        }
                      />
                      <Route
                        path="settings"
                        element={
                          <LazyPage>
                            <SettingsPage />
                          </LazyPage>
                        }
                      />
                    </Route>
                  </Route>
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </BrowserRouter>
            </ToastProvider>
          </AuthProvider>
        </I18nProvider>
      </ThemeProvider>
    </QueryClientProvider>
  )
}
