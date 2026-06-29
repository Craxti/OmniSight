import { api } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import {
  type AuthItemsV1Response,
  type AuthResultV1Response,
  type SessionV1Response,
  type UserV1Response,
  unwrapAuthItems,
  unwrapAuthResult,
  unwrapSession,
  unwrapUser,
} from '@/shared/api/v1Auth'

export const authApi = {
  login: async (email: string, password: string) => {
    const body = await api<SessionV1Response>(paths.auth.login, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    return unwrapSession(body)
  },
  me: async () => {
    const body = await api<UserV1Response>(paths.auth.me)
    return unwrapUser(body)
  },
  changePassword: async (current_password: string, new_password: string) => {
    const body = await api<AuthResultV1Response>(paths.auth.changePassword, {
      method: 'POST',
      body: JSON.stringify({ current_password, new_password }),
    })
    return unwrapAuthResult(body)
  },
  users: async () => {
    const body = await api<AuthItemsV1Response>(paths.auth.users)
    return unwrapAuthItems(body)
  },
  createUser: async (data: { email: string; password: string; role: string }) => {
    const body = await api<UserV1Response>(paths.auth.users, { method: 'POST', body: JSON.stringify(data) })
    return unwrapUser(body)
  },
  updateRole: async (email: string, role: string) => {
    const body = await api<UserV1Response>(paths.auth.userRole(email), {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    })
    return unwrapUser(body)
  },
  updateActive: async (email: string, is_active: boolean) => {
    const body = await api<UserV1Response>(paths.auth.userActive(email), {
      method: 'PATCH',
      body: JSON.stringify({ is_active }),
    })
    return unwrapUser(body)
  },
  resetPassword: async (email: string, password: string) => {
    const body = await api<AuthResultV1Response>(paths.auth.userResetPassword(email), {
      method: 'POST',
      body: JSON.stringify({ password }),
    })
    return unwrapAuthResult(body)
  },
  deleteUser: async (email: string) => {
    const body = await api<AuthResultV1Response>(paths.auth.userEmail(email), { method: 'DELETE' })
    return unwrapAuthResult(body)
  },
}
