import { api, buildQuery, downloadFile, uploadFile } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import type { Relation, RelationCreate } from '@/shared/api/types'
import { omitEmpty } from '@/shared/api/v1Envelope'
import {
  type DeleteResultV1Response,
  type ImportReportV1Response,
  type RelationMutationV1Response,
  type RelationValidationV1Response,
  type RelationsListV1Response,
  type V1Pagination,
  unwrapDeleteResult,
  unwrapImportReport,
  unwrapRelationMutation,
  unwrapRelationValidation,
  unwrapRelationsList,
} from '@/shared/api/v1Inventory'

export type RelationsListParams = {
  page?: number
  page_size?: number
  q?: string
  relation_type?: string
  status?: string
  data_source?: string
  source_name?: string
  target_name?: string
}

export type RelationsListResult = {
  items: Relation[]
  pagination: V1Pagination
}

async function fetchRelationsPage(params: RelationsListParams = {}): Promise<RelationsListResult> {
  const body = await api<RelationsListV1Response>(
    `${paths.relations.list}${buildQuery(
      omitEmpty({ page: 1, page_size: 50, ...params }) as Record<string, string | number>,
    )}`,
  )
  return unwrapRelationsList(body)
}

async function listAllRelations(): Promise<Relation[]> {
  const page_size = 500
  const items: Relation[] = []
  let page = 1
  for (;;) {
    const { items: pageItems, pagination } = await fetchRelationsPage({ page, page_size })
    items.push(...pageItems)
    if (page >= pagination.total_pages) {
      break
    }
    page += 1
  }
  return items
}

export const relationsApi = {
  listPage: fetchRelationsPage,
  listAll: listAllRelations,
  /** @deprecated Use listPage or listAll */
  list: listAllRelations,
  create: async (data: RelationCreate) => {
    const body = await api<RelationMutationV1Response>(paths.relations.list, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return unwrapRelationMutation(body)
  },
  delete: async (id: number) => {
    const body = await api<DeleteResultV1Response>(paths.relations.detail(id), { method: 'DELETE' })
    return unwrapDeleteResult(body)
  },
  bulkDelete: async (relation_ids: number[]) => {
    await Promise.all(
      relation_ids.map(async (id) => {
        const body = await api<DeleteResultV1Response>(paths.relations.detail(id), { method: 'DELETE' })
        return unwrapDeleteResult(body)
      }),
    )
    return { deleted: relation_ids.length }
  },
  bulkStatus: async (relation_ids: number[], status: string) => {
    await Promise.all(
      relation_ids.map(async (id) => {
        const body = await api<RelationMutationV1Response>(paths.relations.detail(id), {
          method: 'PATCH',
          body: JSON.stringify({ status }),
        })
        return unwrapRelationMutation(body)
      }),
    )
    return { updated: relation_ids.length }
  },
  update: async (id: number, data: { relation_type?: string; status?: string; data_source?: string }) => {
    const body = await api<RelationMutationV1Response>(paths.relations.detail(id), {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return unwrapRelationMutation(body)
  },
  validate: async () => {
    const body = await api<RelationValidationV1Response>(paths.relations.validate)
    return unwrapRelationValidation(body)
  },
  exportCsv: () => downloadFile(paths.relations.exportCsv, 'relations.csv'),
  exportXlsx: () => downloadFile(paths.relations.exportXlsx, 'relations.xlsx'),
  importCsv: async (file: File) => {
    const body = await uploadFile<ImportReportV1Response>(paths.relations.importCsv, file)
    return unwrapImportReport(body)
  },
  importJson: async (relations: Array<{
    source_ci_id?: number
    target_ci_id?: number
    source_name?: string
    target_name?: string
    relation_type: string
    status?: string
    data_source?: string
  }>) => {
    const body = await api<ImportReportV1Response>(paths.relations.importJson, {
      method: 'POST',
      body: JSON.stringify({ relations }),
    })
    return unwrapImportReport(body)
  },
}
