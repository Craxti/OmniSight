import { MarkerType, type Edge } from '@xyflow/react'
import type { LocaleMessages } from '@/i18n/locales/en'
import { getRelationVisual, GRAPH_PATH_EDGE_COLOR } from '@/lib/graphVisuals'
import type { GraphPanelData } from '@/shared/api/types'

function relationLabel(labels: LocaleMessages['graph']['relationTypes'], relationType: string): string {
  return (labels as Record<string, string>)[relationType] ?? relationType
}

export function pathEdgeKeysFromPath(path: Array<{ id: number }>): Set<string> {
  const keys = new Set<string>()
  for (let i = 0; i < path.length - 1; i++) {
    keys.add(`${path[i].id}-${path[i + 1].id}`)
    keys.add(`${path[i + 1].id}-${path[i].id}`)
  }
  return keys
}

export function buildGraphEdges(
  g: GraphPanelData,
  opts: {
    t: LocaleMessages
    focusMode: boolean
    relationFilter: string
    pathEdgeKeys: Set<string>
    editable: boolean
  },
): Edge[] {
  const { t, focusMode, relationFilter, pathEdgeKeys, editable } = opts
  return g.edges.map((e) => {
    const dimmed = focusMode && e.relation_type !== relationFilter
    const onPath = pathEdgeKeys.has(`${e.source_ci_id}-${e.target_ci_id}`)
    const visual = getRelationVisual(e.relation_type)
    const stroke = onPath ? GRAPH_PATH_EDGE_COLOR : visual.color

    return {
      id: String(e.id),
      source: String(e.source_ci_id),
      target: String(e.target_ci_id),
      type: 'relationType',
      data: {
        relationType: e.relation_type,
        relationLabel: relationLabel(t.graph.relationTypes, e.relation_type),
        onPath,
        dimmed,
        relationId: e.id,
        sourceCiId: e.source_ci_id,
        targetCiId: e.target_ci_id,
        status: e.status,
        dataSource: e.data_source || 'manual',
      },
      animated: false,
      style: {
        stroke,
        strokeWidth: onPath ? 3 : visual.strokeWidth,
        strokeDasharray: onPath ? 'none' : visual.dash,
        opacity: dimmed ? 0.14 : onPath ? 1 : 0.88,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 14,
        height: 14,
        color: stroke,
      },
      selectable: editable && !dimmed,
      deletable: editable && !dimmed,
    } satisfies Edge
  })
}

export function activeNodeIdsForFilter(
  graph: GraphPanelData,
  rootId: number,
  relationFilter: string,
): Set<number> {
  const focusMode = Boolean(relationFilter)
  const visibleEdges = graph.edges.filter((e) => !relationFilter || e.relation_type === relationFilter)
  const activeNodeIds = new Set<number>()
  if (!focusMode) return activeNodeIds
  activeNodeIds.add(rootId)
  for (const e of visibleEdges) {
    activeNodeIds.add(e.source_ci_id)
    activeNodeIds.add(e.target_ci_id)
  }
  return activeNodeIds
}
