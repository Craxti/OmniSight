import type { AuditEntry, DashboardData } from '@/shared/api/types'
import { type V1Base, type V1Pagination, unwrapV1Field, unwrapV1ListTotal } from '@/shared/api/v1Envelope'

export const OPS_SCHEMA_V1 = 'rsm-ops-v1' as const

export type DashboardV1Response = V1Base & {
  dashboard: DashboardData
}

export type AuditListV1Response = V1Base & {
  items: AuditEntry[]
  pagination: V1Pagination
}

export type AuditItemsV1Response = V1Base & {
  items: AuditEntry[]
  pagination: V1Pagination
}

export const unwrapDashboard = (body: DashboardV1Response) => unwrapV1Field(body, 'dashboard')
export const unwrapAuditList = unwrapV1ListTotal<AuditEntry>
export function unwrapAuditItems(body: AuditItemsV1Response): AuditEntry[] {
  return body.items
}
