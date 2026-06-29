import { api, buildQuery } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import { type DomainConstantsV1Response, unwrapDomainConstants } from '@/shared/api/v1Meta'
import {
  type AuditItemsV1Response,
  type AuditListV1Response,
  type DashboardV1Response,
  unwrapAuditItems,
  unwrapAuditList,
  unwrapDashboard,
} from '@/shared/api/v1Ops'

export const miscApi = {
  dashboard: async () => {
    const body = await api<DashboardV1Response>(paths.misc.dashboard)
    return unwrapDashboard(body)
  },
  audit: async (params?: Record<string, string>) => {
    const skip = Number(params?.skip ?? 0)
    const limit = Number(params?.limit ?? 50)
    const page = Math.floor(skip / limit) + 1
    const filters = Object.fromEntries(
      Object.entries(params ?? {}).filter(([key]) => key !== 'skip' && key !== 'limit'),
    )
    const body = await api<AuditListV1Response>(
      `${paths.misc.audit}${buildQuery({ page, page_size: limit, ...filters })}`,
    )
    return unwrapAuditList(body)
  },
  entityAudit: async (type: string, id: number) => {
    const body = await api<AuditItemsV1Response>(paths.misc.entityAudit(type, id))
    return unwrapAuditItems(body)
  },
  constants: async () => {
    const body = await api<DomainConstantsV1Response>(paths.misc.constants)
    return unwrapDomainConstants(body)
  },
}
