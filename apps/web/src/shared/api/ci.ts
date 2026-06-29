import { api, buildExportQuery, buildQuery, downloadFile, uploadFile } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import type { CI, ImportTypeMappingEntry, ImportTypePreview } from '@/shared/api/types'
import {
  type CiDetailV1Response,
  type CiListV1Response,
  type CiMutationV1Response,
  type DeleteResultV1Response,
  type BulkStatusV1Response,
  type CiTypeListV1Response,
  type CiTypeMutationV1Response,
  type ExportPayloadV1Response,
  type ImportReportV1Response,
  type RelationsListV1Response,
  toV1ListParams,
  unwrapBulkStatusResult,
  unwrapCiDetail,
  unwrapCiList,
  unwrapCiPage,
  unwrapCiMutation,
  unwrapCiTypeMutation,
  unwrapCiTypesList,
  unwrapDeleteResult,
  unwrapExportPayload,
  unwrapImportReport,
} from '@/shared/api/v1Inventory'

export type { ImportTypeMappingEntry, ImportTypePreview } from '@/shared/api/types'

export const ciApi = {
  list: async (params?: Record<string, string | number>) => {
    const body = await api<CiListV1Response>(
      `${paths.ci.list}${buildQuery(toV1ListParams(params))}`,
    )
    return unwrapCiList(body)
  },
  listPage: async (params?: Record<string, string | number>) => {
    const body = await api<CiListV1Response>(
      `${paths.ci.list}${buildQuery(toV1ListParams(params))}`,
    )
    return unwrapCiPage(body)
  },
  get: async (id: number) => {
    const body = await api<CiDetailV1Response>(paths.resources.detail(id))
    return unwrapCiDetail(body)
  },
  relations: async (id: number) => {
    const body = await api<RelationsListV1Response>(paths.resources.relations(id))
    return body.items
  },
  create: async (data: Partial<CI> & { type_id?: number; type_name?: string }) => {
    const body = await api<CiMutationV1Response>(paths.ci.list, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return unwrapCiMutation(body)
  },
  update: async (id: number, data: Partial<CI>) => {
    const body = await api<CiMutationV1Response>(paths.ci.detail(id), {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return unwrapCiMutation(body)
  },
  delete: async (id: number) => {
    const body = await api<DeleteResultV1Response>(paths.ci.detail(id), { method: 'DELETE' })
    return unwrapDeleteResult(body)
  },
  types: async () => {
    const body = await api<CiTypeListV1Response>(paths.ci.types)
    return unwrapCiTypesList(body)
  },
  createType: async (data: { name: string; description?: string; attribute_schema?: unknown }) => {
    const body = await api<CiTypeMutationV1Response>(paths.ci.types, {
      method: 'POST',
      body: JSON.stringify(data),
    })
    return unwrapCiTypeMutation(body)
  },
  updateType: async (id: number, data: { name?: string; description?: string; attribute_schema?: unknown }) => {
    const body = await api<CiTypeMutationV1Response>(paths.ci.type(id), {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
    return unwrapCiTypeMutation(body)
  },
  deleteType: async (id: number) => {
    const body = await api<DeleteResultV1Response>(paths.ci.type(id), { method: 'DELETE' })
    return unwrapDeleteResult(body)
  },
  exportFull: async (params?: Record<string, string | number>) => {
    const body = await api<ExportPayloadV1Response>(
      `${paths.ci.exportFull}${buildExportQuery(params)}`,
    )
    return unwrapExportPayload<unknown>(body)
  },
  exportCsv: (params?: Record<string, string | number>) =>
    downloadFile(paths.ci.exportCsv, 'rsm-export.zip', params),
  exportXlsx: (params?: Record<string, string | number>) =>
    downloadFile(paths.ci.exportXlsx, 'rsm-export.xlsx', params),
  recycleBin: async () => {
    const body = await api<CiListV1Response>(paths.ci.recycleBin)
    return body.items
  },
  restore: async (id: number) => {
    const body = await api<CiMutationV1Response>(paths.ci.restore(id), { method: 'POST' })
    return unwrapCiMutation(body)
  },
  purge: async (id: number) => {
    const body = await api<DeleteResultV1Response>(paths.ci.purge(id), { method: 'DELETE' })
    return unwrapDeleteResult(body)
  },
  bulkStatus: async (ci_ids: number[], status: string) => {
    const body = await api<BulkStatusV1Response>(paths.ci.bulkStatus, {
      method: 'POST',
      body: JSON.stringify({ ci_ids, status }),
    })
    return unwrapBulkStatusResult(body)
  },
  bulkDelete: async (ci_ids: number[]) => {
    await Promise.all(
      ci_ids.map(async (id) => {
        const body = await api<DeleteResultV1Response>(paths.ci.detail(id), { method: 'DELETE' })
        return unwrapDeleteResult(body)
      }),
    )
    return { deleted: ci_ids.length }
  },
  importCsv: async (file: File) => {
    const body = await uploadFile<ImportReportV1Response>(paths.ci.importCsv, file)
    return unwrapImportReport(body)
  },
  importJson: async (items: unknown[]) => {
    const body = await api<ImportReportV1Response>(paths.ci.import, {
      method: 'POST',
      body: JSON.stringify(items),
    })
    return unwrapImportReport(body)
  },
  previewImport: async (items: unknown[]) => {
    const body = await api<ExportPayloadV1Response>(paths.ci.importPreview, {
      method: 'POST',
      body: JSON.stringify(items),
    })
    return unwrapExportPayload<ImportTypePreview>(body)
  },
  importMapped: async (items: unknown[], typeMappings: ImportTypeMappingEntry[]) => {
    const body = await api<ImportReportV1Response>(paths.ci.importMapped, {
      method: 'POST',
      body: JSON.stringify({ items, type_mappings: typeMappings }),
    })
    return unwrapImportReport(body)
  },
}
