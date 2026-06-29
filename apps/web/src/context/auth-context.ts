import { createContext } from 'react'
import type { UserInfo } from '@/shared/api'

export interface AuthContextValue {
  user: UserInfo | null
  loading: boolean
  login: (email: string, password: string) => Promise<UserInfo>
  logout: () => void
  refreshUser: () => Promise<UserInfo>
  isAdmin: boolean
  canEdit: boolean
}

export const AuthContext = createContext<AuthContextValue | null>(null)
