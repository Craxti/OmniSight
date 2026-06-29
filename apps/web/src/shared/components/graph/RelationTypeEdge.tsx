import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  useStore,
  type EdgeProps,
} from '@xyflow/react'

import { getRelationVisual, GRAPH_PATH_EDGE_COLOR } from '@/lib/graphVisuals'

export type RelationEdgeData = {
  relationType: string
  relationLabel?: string
  onPath?: boolean
  dimmed?: boolean
}

/** HTML-метки не масштабируются с zoom SVG — остаются читаемыми при «Вписать». */
export function RelationTypeEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
  animated,
  data,
}: EdgeProps) {
  const edgeData = data as RelationEdgeData | undefined
  const relationType = edgeData?.relationType ?? ''
  const relationLabel = edgeData?.relationLabel ?? relationType
  const onPath = Boolean(edgeData?.onPath)
  const dimmed = Boolean(edgeData?.dimmed)
  const visual = getRelationVisual(relationType)
  const zoom = useStore((s) => s.transform[2])

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  const stroke = onPath ? GRAPH_PATH_EDGE_COLOR : visual.color
  const edgeStyle = {
    ...style,
    stroke,
    strokeWidth: onPath ? 3 : visual.strokeWidth,
    strokeDasharray: onPath ? 'none' : visual.dash,
    opacity: dimmed ? 0.14 : onPath ? 1 : 0.88,
  }

  const marker: EdgeProps['markerEnd'] =
    markerEnd && typeof markerEnd === 'object' && markerEnd !== null && !Array.isArray(markerEnd)
      ? (Object.assign({}, markerEnd, { color: stroke }) as EdgeProps['markerEnd'])
      : markerEnd

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={edgeStyle}
        markerEnd={marker}
        className={onPath ? 'graph-edge-path' : animated ? 'graph-edge-animated' : undefined}
      />
      {relationLabel && !dimmed ? (
        <EdgeLabelRenderer>
          <div
            className={`graph-edge-label nodrag nopan${onPath ? ' graph-edge-label--path' : ''}`}
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px) scale(${1 / zoom})`,
              borderColor: onPath ? GRAPH_PATH_EDGE_COLOR : visual.color,
              color: onPath ? '#ecfdf5' : undefined,
            }}
          >
            {relationLabel}
          </div>
        </EdgeLabelRenderer>
      ) : null}
    </>
  )
}

export const graphEdgeTypes = { relationType: RelationTypeEdge }
