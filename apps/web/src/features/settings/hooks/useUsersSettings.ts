import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useAuth } from '@/context/useAuth'
import { useSettingsMutations } from '@/features/settings/hooks/useSettingsMutations'
import type { useI18n } from '@/context/useI18n'
import { authApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'
import type { UserCreateForm } from '@/features/settings/components/UserCreateModal'

type TFn = ReturnType<typeof useI18n>['t']

export function useUsersSettings(t: TFn) {
  const { isAdmin } = useAuth()
  const { data: users } = useQuery({
    queryKey: queryKeys.users,
    queryFn: authApi.users,
    enabled: isAdmin,
  })
  const [createUserOpen, setCreateUserOpen] = useState(false)
  const [resetEmail, setResetEmail] = useState<string | null>(null)
  const [deleteFor, setDeleteFor] = useState<string | null>(null)

  const { createUserMut, roleMut, activeMut, deleteUserMut, resetMut } = useSettingsMutations(t)

  const openCreateUser = () => setCreateUserOpen(true)

  const openResetPassword = (email: string) => setResetEmail(email)

  const submitCreateUser = (data: UserCreateForm) => {
    createUserMut.mutate(data, { onSuccess: () => setCreateUserOpen(false) })
  }

  const submitResetPassword = (password: string) => {
    if (!resetEmail) return
    resetMut.mutate(
      { email: resetEmail, password },
      { onSuccess: () => setResetEmail(null) },
    )
  }

  return {
    users,
    createUserOpen,
    setCreateUserOpen,
    resetEmail,
    setResetEmail,
    deleteFor,
    setDeleteFor,
    createUserMut,
    roleMut,
    activeMut,
    deleteUserMut,
    resetMut,
    openCreateUser,
    openResetPassword,
    submitCreateUser,
    submitResetPassword,
  }
}
