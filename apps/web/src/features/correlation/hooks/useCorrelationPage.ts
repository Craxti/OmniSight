import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { useMemo, useState } from 'react'
import { useI18n } from '@/context/useI18n'
import { correlationApi } from '@/shared/api'
import { omitFalsyValues } from '@/shared/api/v1Envelope'
import { downloadBlob } from '@/shared/api/client'
import type { CorrelationContextPayload, CorrelationIngestResponse } from '@/shared/api/types'
import type { AlertRow } from '@/shared/constants'
import type { GraphPanelData } from '@/shared/api/types'

const emptyAlert = (): AlertRow => ({})

export function cleanedAlerts(alerts: AlertRow[]) {
  return alerts.map((a) => omitFalsyValues(a))
}

export function useCorrelationPage() {
  const { t } = useI18n()
  const [alerts, setAlerts] = useState<AlertRow[]>([emptyAlert()])
  const [ingestResult, setIngestResult] = useState<CorrelationIngestResponse | null>(null)

  const ingestMut = useApiMutation<CorrelationIngestResponse, void>({
    mutationFn: () => correlationApi.ingest(cleanedAlerts(alerts), 'ui'),
    messages: { success: t.correlation.toastIngest, error: t.common.error },
    onSuccess: (r) => setIngestResult(r),
  })

  const correlationPayload: CorrelationContextPayload | null = ingestResult?.correlation ?? null

  const correlationGraph = useMemo((): GraphPanelData | null => {
    const g = correlationPayload?.graph
    if (!g?.nodes?.length) return null
    return { nodes: g.nodes, edges: g.edges ?? [] }
  }, [correlationPayload])

  const rootCauseRootId = useMemo(() => {
    const zone = correlationPayload?.potential_root_cause_zone
    if (zone?.length) return zone[0].id
    return correlationGraph?.nodes[0]?.id
  }, [correlationPayload, correlationGraph])

  const rootCauseZoneIds = useMemo(
    () => correlationPayload?.potential_root_cause_zone?.map((ci) => ci.id) ?? [],
    [correlationPayload],
  )

  const alertResourceIds = useMemo(
    () => correlationPayload?.resource_ids ?? [],
    [correlationPayload],
  )

  const correlationPathEdgeKeys = useMemo(() => {
    if (!correlationGraph?.edges?.length) return []
    const highlighted = new Set([...alertResourceIds, ...rootCauseZoneIds])
    if (!highlighted.size) return []
    return correlationGraph.edges
      .filter(
        (e) =>
          e.relation_type === 'depends_on' &&
          highlighted.has(e.source_ci_id) &&
          highlighted.has(e.target_ci_id),
      )
      .map((e) => `${e.source_ci_id}-${e.target_ci_id}`)
  }, [correlationGraph, alertResourceIds, rootCauseZoneIds])

  const exportJson = () => {
    if (!ingestResult) return
    downloadBlob(
      new Blob([JSON.stringify(ingestResult, null, 2)], { type: 'application/json' }),
      'correlation-result.json',
    )
  }

  const ambiguousCount = ingestResult?.resolve.resolved.filter((r) => r.ambiguous).length ?? 0

  const staleContext =
    (ingestResult?.resolve.resolved.length ?? 0) > 0 &&
    !(correlationPayload?.enrichment?.length) &&
    !(correlationPayload?.graph?.nodes?.length)

  return {
    t,
    alerts,
    setAlerts,
    ingestResult,
    ingestMut,
    correlationPayload,
    correlationGraph,
    rootCauseRootId,
    rootCauseZoneIds,
    alertResourceIds,
    correlationPathEdgeKeys,
    exportJson,
    ambiguousCount,
    staleContext,
  }
}
