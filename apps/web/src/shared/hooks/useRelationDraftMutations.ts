import type { RelationCreate } from '@/shared/api/types'
import { DEFAULT_RELATION_STATUS } from '@/shared/constants'
import type { useRelationMutations } from '@/shared/hooks/useRelationMutations'

export type RelationCreateDraft = {
  sourceCiId: number
  targetCiId: number
  relationType: string
  dataSource: string
}

export type RelationEditDraft = RelationCreateDraft & {
  id: number
  status: string
}

type SnakeCreateForm = {
  source_ci_id: string | number
  target_ci_id: string | number
  relation_type: string
  data_source: string
}

type SnakeEditForm = {
  id: number
  relation_type: string
  status: string
  data_source: string
}

type Mutations = Pick<ReturnType<typeof useRelationMutations>, 'createMut' | 'updateMut' | 'deleteMut'>

function toCreatePayload(draft: RelationCreateDraft | SnakeCreateForm): RelationCreate {
  if ('sourceCiId' in draft) {
    return {
      source_ci_id: draft.sourceCiId,
      target_ci_id: draft.targetCiId,
      relation_type: draft.relationType,
      status: DEFAULT_RELATION_STATUS,
      data_source: draft.dataSource,
    }
  }
  return {
    source_ci_id: Number(draft.source_ci_id),
    target_ci_id: Number(draft.target_ci_id),
    relation_type: draft.relation_type,
    status: DEFAULT_RELATION_STATUS,
    data_source: draft.data_source,
  }
}

function toUpdateBody(draft: RelationEditDraft | SnakeEditForm) {
  const relationType = 'relationType' in draft ? draft.relationType : draft.relation_type
  const dataSource = 'dataSource' in draft ? draft.dataSource : draft.data_source
  return {
    relation_type: relationType,
    status: draft.status,
    data_source: dataSource || undefined,
  }
}

/** Adapts relation draft forms to snake_case API payloads. */
export function useRelationDraftMutations(
  mutations: Mutations,
  options?: {
    onCreateSuccess?: (draft: RelationCreateDraft | SnakeCreateForm) => void
    onUpdateSuccess?: (draft: RelationEditDraft | SnakeEditForm) => void
    onDeleteSuccess?: () => void
    onDeleteError?: () => void
  },
) {
  const { createMut, updateMut, deleteMut } = mutations

  const createDraftMut = {
    ...createMut,
    mutate: (draft: RelationCreateDraft | SnakeCreateForm, mutateOptions?: Parameters<typeof createMut.mutate>[1]) =>
      createMut.mutate(toCreatePayload(draft), {
        ...mutateOptions,
        onSuccess: (...args) => {
          options?.onCreateSuccess?.(draft)
          mutateOptions?.onSuccess?.(...args)
        },
      }),
  }

  const updateDraftMut = {
    ...updateMut,
    mutate: (draft: RelationEditDraft | SnakeEditForm, mutateOptions?: Parameters<typeof updateMut.mutate>[1]) =>
      updateMut.mutate(
        { id: draft.id, body: toUpdateBody(draft) },
        {
          ...mutateOptions,
          onSuccess: (...args) => {
            options?.onUpdateSuccess?.(draft)
            mutateOptions?.onSuccess?.(...args)
          },
        },
      ),
  }

  const deleteDraftMut = {
    ...deleteMut,
    mutate: (relationId: number, mutateOptions?: Parameters<typeof deleteMut.mutate>[1]) =>
      deleteMut.mutate(relationId, {
        ...mutateOptions,
        onSuccess: (...args) => {
          options?.onDeleteSuccess?.()
          mutateOptions?.onSuccess?.(...args)
        },
        onError: (...args) => {
          options?.onDeleteError?.()
          mutateOptions?.onError?.(...args)
        },
      }),
  }

  return { createDraftMut, updateDraftMut, deleteDraftMut }
}
