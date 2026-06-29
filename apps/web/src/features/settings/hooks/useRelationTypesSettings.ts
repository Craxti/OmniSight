import { useState } from 'react'
import { useSettingsMutations } from '@/features/settings/hooks/useSettingsMutations'
import type { RelationTypeFormState } from '@/features/settings/components/RelationTypeFormModal'
import type { useI18n } from '@/context/useI18n'

type TFn = ReturnType<typeof useI18n>['t']

export function useRelationTypesSettings(t: TFn) {
  const [relationTypeFormInitial, setRelationTypeFormInitial] = useState<RelationTypeFormState | null>(null)
  const [relationTypeFormOpen, setRelationTypeFormOpen] = useState(false)
  const { saveRelationTypeMut, deleteRelationTypeMut } = useSettingsMutations(t)

  const openEditRelationType = (relationType: {
    id: number
    name: string
    description?: string
    is_official?: boolean
  }) => {
    setRelationTypeFormInitial({
      id: relationType.id,
      name: relationType.name,
      description: relationType.description || '',
      isOfficial: relationType.is_official,
    })
    setRelationTypeFormOpen(true)
  }

  const openNewRelationType = () => {
    setRelationTypeFormInitial({ name: '', description: '' })
    setRelationTypeFormOpen(true)
  }

  const closeRelationTypeForm = () => {
    setRelationTypeFormOpen(false)
    setRelationTypeFormInitial(null)
  }

  const saveRelationType = (form: RelationTypeFormState) => {
    saveRelationTypeMut.mutate(form, { onSuccess: closeRelationTypeForm })
  }

  return {
    relationTypeFormInitial,
    relationTypeFormOpen,
    saveRelationTypeMut,
    deleteRelationTypeMut,
    openEditRelationType,
    openNewRelationType,
    closeRelationTypeForm,
    saveRelationType,
  }
}
