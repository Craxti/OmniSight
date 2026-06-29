import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'

import DashboardPageSkeleton from '@/components/PageLoader'

export default function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) {
    return <DashboardPageSkeleton />
  }
  if (!user) return <Navigate to="/login" replace />
  const onChangePassword = location.pathname === '/change-password'
  if (user.must_change_password && !onChangePassword) {
    return <Navigate to="/change-password" replace />
  }
  if (!user.must_change_password && onChangePassword) {
    return <Navigate to="/" replace />
  }
  return <Outlet />
}
