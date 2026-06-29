import { useEffect, useState, type ReactNode } from 'react'
import { authApi, clearToken, getToken, setToken } from '@/shared/api'
import type { UserInfo } from '@/shared/api'
import { AuthContext } from '@/context/auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setLoading(false)
      return
    }
    authApi
      .me()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false))

    const onUnauthorized = () => setUser(null)
    window.addEventListener('auth:unauthorized', onUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', onUnauthorized)
  }, [])

  const refreshUser = async () => {
    const me = await authApi.me()
    setUser(me)
    return me
  }

  const login = async (email: string, password: string) => {
    const { access_token } = await authApi.login(email, password)
    setToken(access_token)
    return refreshUser()
  }

  const logout = () => {
    clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        refreshUser,
        isAdmin: user?.role === 'admin',
        canEdit: user?.role === 'admin' || user?.role === 'editor',
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
