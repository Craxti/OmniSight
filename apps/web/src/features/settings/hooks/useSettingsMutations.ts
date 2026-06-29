import { useApiMutation } from '@/shared/hooks/useApiMutation'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'
import { authApi, ciApi } from '@/shared/api'
import { relationTypesApi } from '@/shared/api/relationTypes'
import { queryKeys } from '@/shared/queryKeys'

type Messages = (typeof messages)[Locale]

export function useSettingsMutations(t: Messages) {
  const createUserMut = useApiMutation({
    mutationFn: (data: { email: string; password: string; role: string }) => authApi.createUser(data),
    invalidateKeys: [queryKeys.users],
    messages: { success: t.settings.toastUserCreated, error: t.common.error },
  })

  const roleMut = useApiMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) => authApi.updateRole(email, role),
    invalidateKeys: [queryKeys.users],
    messages: { success: t.settings.toastRoleUpdated, error: t.common.error },
  })

  const activeMut = useApiMutation({
    mutationFn: ({ email, is_active }: { email: string; is_active: boolean }) =>
      authApi.updateActive(email, is_active),
    invalidateKeys: [queryKeys.users],
    messages: { success: t.settings.toastUserActivated, error: t.common.error },
    getSuccessMessage: (_data, { is_active }) =>
      is_active ? t.settings.toastUserActivated : t.settings.toastUserDeactivated,
  })

  const deleteUserMut = useApiMutation({
    mutationFn: (email: string) => authApi.deleteUser(email),
    invalidateKeys: [queryKeys.users],
    messages: { success: t.settings.toastUserDeleted, error: t.common.error },
  })

  const resetMut = useApiMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.resetPassword(email, password),
    messages: { success: t.settings.toastPasswordReset, error: t.common.error },
  })

  const saveTypeMut = useApiMutation({
    mutationFn: async (typeForm: { id?: number; name: string; description: string; schemaJson: string }) => {
      let schema: unknown = { properties: {} }
      if (typeForm.schemaJson.trim()) {
        schema = JSON.parse(typeForm.schemaJson)
      }
      const payload = { name: typeForm.name, description: typeForm.description || undefined, attribute_schema: schema }
      if (typeForm.id) return ciApi.updateType(typeForm.id, payload)
      return ciApi.createType(payload)
    },
    invalidateKeys: [queryKeys.ci.types],
    messages: { success: t.settings.toastTypeSaved, error: t.common.error },
  })

  const deleteTypeMut = useApiMutation({
    mutationFn: (id: number) => ciApi.deleteType(id),
    invalidateKeys: [queryKeys.ci.types],
    messages: { success: t.settings.toastTypeDeleted, error: t.common.error },
  })

  const saveRelationTypeMut = useApiMutation({
    mutationFn: async (typeForm: { id?: number; name: string; description: string }) => {
      const payload = { name: typeForm.name, description: typeForm.description || undefined }
      if (typeForm.id) return relationTypesApi.update(typeForm.id, payload)
      return relationTypesApi.create(payload)
    },
    invalidateKeys: [queryKeys.relations.relationTypes, queryKeys.meta.constants],
    messages: { success: t.settings.toastRelationTypeSaved, error: t.common.error },
  })

  const deleteRelationTypeMut = useApiMutation({
    mutationFn: (id: number) => relationTypesApi.delete(id),
    invalidateKeys: [queryKeys.relations.relationTypes, queryKeys.meta.constants],
    messages: { success: t.settings.toastRelationTypeDeleted, error: t.common.error },
  })

  return {
    createUserMut,
    roleMut,
    activeMut,
    deleteUserMut,
    resetMut,
    saveTypeMut,
    deleteTypeMut,
    saveRelationTypeMut,
    deleteRelationTypeMut,
  }
}
