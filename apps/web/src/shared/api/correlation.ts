import { api, buildQuery } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import type {
  CorrelationContextResponse,
  CorrelationIngestLogDetail,
  CorrelationIngestLogStats,
  CorrelationIngestLogSummary,
  CorrelationIngestResponse,
  CorrelationResolveResponse,
} from '@/shared/api/types'
import { type V1Base, type V1Pagination, unwrapV1Field, unwrapV1ListTotal } from '@/shared/api/v1Envelope'

type V1Envelope = {
  api_version?: string
  schema_version?: string
}

type CorrelationIngestLogListV1Response = V1Base & {
  items: CorrelationIngestLogSummary[]
  pagination: V1Pagination
  stats: CorrelationIngestLogStats
}

type CorrelationIngestLogDetailV1Response = V1Base & {
  ingest_log: CorrelationIngestLogDetail
}

export const correlationApi = {
  ingest: async (alerts: Record<string, string>[], source?: string) => {
    const body = await api<CorrelationIngestResponse & V1Envelope>(paths.correlation.ingest, {
      method: 'POST',
      body: JSON.stringify({ alerts, source, depth: 3, page: 1, page_size: 100 }),
    })
    return body
  },
  ingestLogs: async (params?: { page?: number; page_size?: number; source?: string }) => {
    const body = await api<CorrelationIngestLogListV1Response>(
      `${paths.correlation.ingestLogs}${buildQuery(params ?? {})}`,
    )
    const { items, total } = unwrapV1ListTotal<CorrelationIngestLogSummary>(body)
    return { items, total, stats: body.stats }
  },
  ingestLog: async (id: number) => {
    const body = await api<CorrelationIngestLogDetailV1Response>(paths.correlation.ingestLog(id))
    return unwrapV1Field(body, 'ingest_log')
  },
  resolve: async (alerts: Record<string, string>[]) => {
    const body = await api<CorrelationResolveResponse & V1Envelope>(paths.resources.resolve, {
      method: 'POST',
      body: JSON.stringify({ alerts, page: 1, page_size: 100 }),
    })
    return body
  },
  context: async (resource_ids: number[]) => {
    const body = await api<CorrelationContextResponse & V1Envelope>(paths.correlation.context, {
      method: 'POST',
      body: JSON.stringify({ resource_ids, depth: 3 }),
    })
    return body
  },
}
