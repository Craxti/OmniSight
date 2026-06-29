import type { CI, CIDetail, ImportReport, Relation, RelationValidationResult } from '@/shared/api/types'
import {
  type V1Base,
  type V1Pagination,
  omitEmpty,
  toV1ListParams,
  unwrapV1Field,
  unwrapV1ListTotal,
  unwrapV1PagedItems,
  unwrapV1Result,
} from '@/shared/api/v1Envelope'

export const INVENTORY_SCHEMA_V1 = 'rsm-inventory-v1' as const

export type { V1Base, V1Pagination }
export { toV1ListParams, omitEmpty }

export type CiListV1Response = V1Base & {
  items: CI[]
  pagination: V1Pagination
}

export type CiDetailV1Response = V1Base & {
  ci: CIDetail
}

export type CiMutationV1Response = V1Base & {
  ci: CI
}

export type RelationsListV1Response = V1Base & {
  items: Relation[]
  pagination: V1Pagination
}

export type RelationDetailV1Response = V1Base & {
  relation: Relation
}

export type RelationMutationV1Response = V1Base & {
  relation: Relation
}

export type RelationValidationV1Response = V1Base & {
  validation: RelationValidationResult
}

export type DeleteResultV1Response = V1Base & {
  result: { ok: boolean }
}

export type BulkStatusV1Response = V1Base & {
  result: { updated: number }
}

export type ImportReportV1Response = V1Base & {
  report: ImportReport
}

export type ExportPayloadV1Response = V1Base & {
  export: unknown
}

export type CiType = {
  id: number
  name: string
  description?: string
  attribute_schema?: unknown
  is_official?: boolean
  is_import_draft?: boolean
}

export type CiTypeListV1Response = V1Base & {
  items: CiType[]
  pagination: V1Pagination
}

export type CiTypeMutationV1Response = V1Base & {
  ci_type: CiType
}

export type RelationType = {
  id: number
  name: string
  description?: string
  is_official?: boolean
}

export type RelationTypeListV1Response = V1Base & {
  items: RelationType[]
  pagination: V1Pagination
}

export type RelationTypeMutationV1Response = V1Base & {
  relation_type: RelationType
}

export type ResourceSearchV1Response = V1Base & {
  search: {
    items: CI[]
    total: number
    match_mode: string
  }
}

export const unwrapCiList = unwrapV1ListTotal<CI>
export const unwrapCiPage = unwrapV1PagedItems<CI>
export const unwrapCiDetail = (body: CiDetailV1Response) => unwrapV1Field(body, 'ci')
export const unwrapCiMutation = (body: CiMutationV1Response) => unwrapV1Field(body, 'ci')
export const unwrapRelationsPage = unwrapV1PagedItems<Relation>
export const unwrapRelationsList = unwrapV1PagedItems<Relation>
export const unwrapRelationMutation = (body: RelationMutationV1Response) => unwrapV1Field(body, 'relation')
export const unwrapRelationValidation = (body: RelationValidationV1Response) => unwrapV1Field(body, 'validation')
export const unwrapDeleteResult = unwrapV1Result
export const unwrapBulkStatusResult = (body: BulkStatusV1Response) => body.result
export const unwrapImportReport = (body: ImportReportV1Response): ImportReport => ({
  ...body.report,
  errors: body.report.errors ?? [],
})
export const unwrapExportPayload = <T>(body: ExportPayloadV1Response): T => body.export as T
export function unwrapCiTypesList(body: CiTypeListV1Response): CiType[] {
  return body.items
}
export const unwrapCiTypeMutation = (body: CiTypeMutationV1Response) => unwrapV1Field(body, 'ci_type')
export function unwrapRelationTypesList(body: RelationTypeListV1Response): RelationType[] {
  return body.items
}
export const unwrapRelationTypeMutation = (body: RelationTypeMutationV1Response) =>
  unwrapV1Field(body, 'relation_type')
export const unwrapResourceSearch = (body: ResourceSearchV1Response) => unwrapV1Field(body, 'search')
