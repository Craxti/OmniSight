import { ReactFlowProvider } from '@xyflow/react'
import { useMemo } from 'react'
import { GraphCanvas } from '@/shared/components/graph/GraphCanvas'
import type { GraphPanelData } from '@/shared/api/types'

type Props = {
  graph: GraphPanelData
  rootId?: number
  rootCauseIds?: number[]
  alertResourceIds?: number[]
  pathEdgeKeys?: string[]
  className?: string
  minHeight?: string
  emphasizeHighlighted?: boolean
  rootBadge?: string
  alertBadge?: string
}

/** Read-only graph panel — shared by Graph page and Correlation. */
export function EmbeddedGraphView({
  graph,
  rootId,
  rootCauseIds,
  alertResourceIds,
  pathEdgeKeys,
  className = '',
  minHeight = '18rem',
  emphasizeHighlighted = false,
  rootBadge,
  alertBadge,
}: Props) {
  const empty = useMemo(() => new Set<number>(), [])
  const emptyKeys = useMemo(() => new Set<string>(), [])
  const resolvedRoot = rootId ?? graph.nodes[0]?.id ?? 0

  const rootCauseSet = useMemo(
    () => new Set(rootCauseIds ?? (rootId != null ? [rootId] : [])),
    [rootCauseIds, rootId],
  )
  const alertSet = useMemo(() => new Set(alertResourceIds ?? []), [alertResourceIds])
  const pathKeys = useMemo(() => new Set(pathEdgeKeys ?? []), [pathEdgeKeys])

  if (!graph.nodes.length) return null

  return (
    <div
      className={`graph-flow-panel overflow-hidden ${className}`}
      style={{ minHeight, height: minHeight }}
    >
      <ReactFlowProvider>
        <GraphCanvas
          rootId={resolvedRoot}
          depth={3}
          relationFilter=""
          graph={graph}
          pathIds={empty}
          pathEdgeKeys={pathKeys.size ? pathKeys : emptyKeys}
          impactIds={empty}
          componentIds={empty}
          rootCauseIds={rootCauseSet}
          alertResourceIds={alertSet}
          emphasizeHighlighted={emphasizeHighlighted}
          useSavedLayout={false}
          showLegend={false}
          fitViewPadding={0.12}
          isLoading={false}
          nodeBadges={{ rootBadge, alertBadge }}
        />
      </ReactFlowProvider>
    </div>
  )
}
