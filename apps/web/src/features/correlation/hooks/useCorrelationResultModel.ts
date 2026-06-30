import { useMemo } from 'react'
import type { CorrelationContextPayload, CorrelationIngestResponse } from '@/shared/api/types'
import type { GraphPanelData } from '@/shared/api/types'

export function useCorrelationResultModel(ingestResult: CorrelationIngestResponse | null) {
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

  const ambiguousCount = ingestResult?.resolve.resolved.filter((r) => r.ambiguous).length ?? 0

  const staleContext =
    (ingestResult?.resolve.resolved.length ?? 0) > 0 &&
    !(correlationPayload?.enrichment?.length) &&
    !(correlationPayload?.graph?.nodes?.length)

  return {
    correlationPayload,
    correlationGraph,
    rootCauseRootId,
    rootCauseZoneIds,
    alertResourceIds,
    correlationPathEdgeKeys,
    ambiguousCount,
    staleContext,
    chainRelated: ingestResult?.correlation?.chain_related ?? false,
  }
}
