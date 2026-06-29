import { api } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import type { CorrelationContextResponse, CorrelationIngestResponse, CorrelationResolveResponse } from '@/shared/api/types'

type V1Envelope = {
  api_version?: string
  schema_version?: string
}

export const correlationApi = {
  ingest: async (alerts: Record<string, string>[], source?: string) => {
    const body = await api<CorrelationIngestResponse & V1Envelope>(paths.correlation.ingest, {
      method: 'POST',
      body: JSON.stringify({ alerts, source, depth: 3, page: 1, page_size: 100 }),
    })
    return body
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
