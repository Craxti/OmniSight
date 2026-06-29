import { api } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import {
  type DeleteResultV1Response,
  type RelationTypeListV1Response,
  type RelationTypeMutationV1Response,
  unwrapDeleteResult,
  unwrapRelationTypeMutation,
  unwrapRelationTypesList,
} from '@/shared/api/v1Inventory'

export const relationTypesApi = {
  list: async () => {
    const body = await api<RelationTypeListV1Response>(paths.relations.types)
    return unwrapRelationTypesList(body)
  },
  create: async (data: { name: string; description?: string }) => {
    const body = await api<RelationTypeMutationV1Response>(paths.relations.types, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return unwrapRelationTypeMutation(body)
  },
  update: async (id: number, data: { name?: string; description?: string }) => {
    const body = await api<RelationTypeMutationV1Response>(paths.relations.type(id), {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return unwrapRelationTypeMutation(body)
  },
  delete: async (id: number) => {
    const body = await api<DeleteResultV1Response>(paths.relations.type(id), { method: 'DELETE' })
    return unwrapDeleteResult(body)
  },
}
