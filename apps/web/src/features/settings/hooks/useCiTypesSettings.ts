import { useState } from 'react'
import { useSettingsMutations } from '@/features/settings/hooks/useSettingsMutations'
import type { CiTypeFormState } from '@/features/settings/components/CiTypeFormModal'
import type { useI18n } from '@/context/useI18n'

type TFn = ReturnType<typeof useI18n>['t']

export type TypeFormState = CiTypeFormState

export function useCiTypesSettings(t: TFn) {
  const [typeFormInitial, setTypeFormInitial] = useState<CiTypeFormState | null>(null)
  const [typeFormOpen, setTypeFormOpen] = useState(false)
  const { saveTypeMut, deleteTypeMut } = useSettingsMutations(t)

  const openEditType = (ciType: {
    id: number
    name: string
    description?: string
    attribute_schema?: unknown
  }) => {
    setTypeFormInitial({
      id: ciType.id,
      name: ciType.name,
      description: ciType.description || '',
      schemaJson: JSON.stringify(ciType.attribute_schema || { properties: {} }, null, 2),
    })
    setTypeFormOpen(true)
  }

  const openNewType = () => {
    setTypeFormInitial({ name: '', description: '', schemaJson: '{\n  "properties": {}\n}' })
    setTypeFormOpen(true)
  }

  const closeTypeForm = () => {
    setTypeFormOpen(false)
    setTypeFormInitial(null)
  }

  const saveType = (typeForm: CiTypeFormState) => {
    saveTypeMut.mutate(typeForm, { onSuccess: closeTypeForm })
  }

  return {
    typeFormInitial,
    typeFormOpen,
    saveTypeMut,
    deleteTypeMut,
    openEditType,
    openNewType,
    closeTypeForm,
    saveType,
  }
}
