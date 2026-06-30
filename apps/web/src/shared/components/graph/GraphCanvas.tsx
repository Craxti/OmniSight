import {
  Background,
  ConnectionMode,
  Controls,
  type Connection,
  ReactFlow,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Edge,
  type Node,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useCallback, useEffect, useImperativeHandle, useRef, forwardRef } from 'react'
import { useI18n } from '@/context/useI18n'
import { GraphCanvasSkeleton } from '@/components/ui'
import { computeGraphLayout, computeOverviewLayout, graphFlowDefaults } from '@/lib/graphLayout'
import type { GraphPanelData } from '@/shared/api/types'
import { activeNodeIdsForFilter, buildGraphEdges } from '@/shared/graph/graphCanvasModel'
import { useGraphLayout } from '@/shared/hooks/useGraphLayout'
import { GraphLegendHelp } from '@/shared/components/graph/GraphLegendHelp'
import { graphEdgeTypes } from '@/shared/components/graph/RelationTypeEdge'
import { graphNodeTypes } from '@/shared/components/graph/ResourceNode'

export type GraphCanvasHandle = {
  fit: () => void
  relayout: () => void
}

export type GraphEdgeEditData = {
  id: number
  sourceCiId: number
  targetCiId: number
  relationType: string
  status: string
  dataSource: string
}

type Props = {
  rootId: number
  depth: number
  relationFilter: string
  graph: GraphPanelData | undefined
  pathIds: Set<number>
  pathEdgeKeys: Set<string>
  impactIds: Set<number>
  componentIds: Set<number>
  rootCauseIds?: Set<number>
  alertResourceIds?: Set<number>
  emphasizeHighlighted?: boolean
  useSavedLayout?: boolean
  overviewLayout?: boolean
  showLegend?: boolean
  fitViewPadding?: number
  nodeBadges?: { rootBadge?: string; alertBadge?: string }
  isLoading: boolean
  editable?: boolean
  onSelectRoot?: (id: number) => void
  onOpenCi?: (id: number) => void
  onStatsChange?: (stats: { nodes: number; edges: number }) => void
  onCreateRelationRequest?: (sourceCiId: number, targetCiId: number) => void
  onEditRelationRequest?: (edge: GraphEdgeEditData) => void
  onDeleteRelationRequest?: (relationId: number) => void
}

export const GraphCanvas = forwardRef<GraphCanvasHandle, Props>(function GraphCanvas(
  {
    rootId,
    depth,
    relationFilter,
    graph,
    pathIds,
    pathEdgeKeys,
    impactIds,
    componentIds,
    rootCauseIds,
    alertResourceIds,
    emphasizeHighlighted = false,
    useSavedLayout = true,
    overviewLayout = false,
    showLegend = true,
    fitViewPadding = 0.24,
    nodeBadges,
    isLoading,
    editable = false,
    onSelectRoot,
    onOpenCi,
    onStatsChange,
    onCreateRelationRequest,
    onEditRelationRequest,
    onDeleteRelationRequest,
  },
  ref,
) {
  const { t } = useI18n()
  const gridColor = 'var(--graph-grid-color)'
  const { fitView, getNodes } = useReactFlow()
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])
  const dataKeyRef = useRef('')
  const clickTimerRef = useRef<number | undefined>(undefined)

  const { savedPositions: loadedPositions, persistPositions, clearPositions } = useGraphLayout(
    rootId,
    relationFilter,
    useSavedLayout && Boolean(graph?.nodes?.length),
  )
  const savedPositions = useSavedLayout ? loadedPositions : null
  const focusMode = Boolean(relationFilter)

  const buildEdges = useCallback(
    (g: GraphPanelData) =>
      buildGraphEdges(g, { t, focusMode, relationFilter, pathEdgeKeys, editable }),
    [editable, focusMode, pathEdgeKeys, relationFilter, t],
  )

  const handleEdgesDelete = useCallback(
    (deleted: Edge[]) => {
      if (!editable) return
      for (const edge of deleted) {
        const relationId = (edge.data as { relationId?: number } | undefined)?.relationId
        if (relationId) onDeleteRelationRequest?.(relationId)
      }
    },
    [editable, onDeleteRelationRequest],
  )

  const handleConnect = useCallback(
    (connection: Connection) => {
      if (!editable) return
      const sourceCiId = Number(connection.source)
      const targetCiId = Number(connection.target)
      if (!sourceCiId || !targetCiId || sourceCiId === targetCiId) return
      onCreateRelationRequest?.(sourceCiId, targetCiId)
    },
    [editable, onCreateRelationRequest],
  )

  const isValidConnection = useCallback(
    (connection: Edge | Connection) => {
      if (!editable) return false
      const source = connection.source
      const target = connection.target
      return Boolean(source && target && source !== target)
    },
    [editable],
  )

  const handleFit = useCallback(() => {
    fitView({ padding: fitViewPadding, duration: 400 })
  }, [fitView, fitViewPadding])

  const computeLayout = useCallback(
    (g: GraphPanelData) =>
      overviewLayout
        ? computeOverviewLayout(g.nodes, g.edges)
        : computeGraphLayout(g.nodes, g.edges, rootId),
    [overviewLayout, rootId],
  )

  const relayout = useCallback(async () => {
    if (!graph?.nodes?.length) return
    if (editable) await clearPositions()
    const { positions } = computeLayout(graph)
    setNodes((ns) =>
      ns.map((n) => ({
        ...n,
        position: positions.get(Number(n.id)) ?? n.position,
      })),
    )
    window.setTimeout(() => fitView({ padding: fitViewPadding, duration: 500 }), 80)
  }, [graph, computeLayout, setNodes, fitView, fitViewPadding, clearPositions, editable])

  const handlePersistPositions = useCallback(() => {
    if (!editable) return
    const positions = Object.fromEntries(getNodes().map((n) => [n.id, n.position]))
    persistPositions(positions)
  }, [editable, getNodes, persistPositions])

  useImperativeHandle(ref, () => ({ fit: handleFit, relayout }), [handleFit, relayout])

  useEffect(() => {
    if (!graph?.nodes?.length) {
      setNodes([])
      setEdges([])
      onStatsChange?.({ nodes: 0, edges: 0 })
      return
    }

    const dataKey = `${rootId}-${depth}-${relationFilter}-${overviewLayout ? 'overview' : 'root'}`
    const sameGraph = dataKeyRef.current === dataKey
    dataKeyRef.current = dataKey

    const { positions } = computeLayout(graph)

    const visibleEdges = graph.edges.filter((e) => !relationFilter || e.relation_type === relationFilter)
    const activeNodeIds = activeNodeIdsForFilter(graph, rootId, relationFilter)

    const nextEdges = buildEdges(graph)

    const highlightedIds = new Set<number>([
      ...(rootCauseIds ?? []),
      ...(alertResourceIds ?? []),
    ])

    setNodes(
      graph.nodes.map((n) => {
        const inRootCause = rootCauseIds ? rootCauseIds.has(n.id) : n.id === rootId
        const inAlert = alertResourceIds?.has(n.id) ?? false
        return {
          id: String(n.id),
          type: 'resource',
          position: savedPositions?.[String(n.id)] ?? positions.get(n.id) ?? { x: 0, y: 0 },
          data: {
            label: n.name,
            type: n.type,
            onPath: pathIds.has(n.id),
            isRoot: inRootCause,
            inAlert,
            inImpact: impactIds.has(n.id),
            inComponents: componentIds.has(n.id),
            rootBadge: nodeBadges?.rootBadge,
            alertBadge: nodeBadges?.alertBadge,
            editable,
            dimmed:
              (focusMode && !activeNodeIds.has(n.id)) ||
              (emphasizeHighlighted && highlightedIds.size > 0 && !highlightedIds.has(n.id)),
          },
          draggable: editable,
          selectable: true,
          connectable: editable,
        }
      }),
    )

    setEdges(nextEdges)
    onStatsChange?.({
      nodes: graph.nodes.length,
      edges: focusMode ? visibleEdges.length : nextEdges.length,
    })

    if (!sameGraph || !savedPositions) {
      const timer = window.setTimeout(
        () => fitView({ padding: fitViewPadding, duration: sameGraph ? 280 : 550 }),
        60,
      )
      return () => window.clearTimeout(timer)
    }
  }, [
    graph,
    rootId,
    depth,
    relationFilter,
    overviewLayout,
    computeLayout,
    focusMode,
    pathIds,
    pathEdgeKeys,
    impactIds,
    componentIds,
    rootCauseIds,
    alertResourceIds,
    emphasizeHighlighted,
    editable,
    buildEdges,
    setNodes,
    setEdges,
    fitView,
    fitViewPadding,
    nodeBadges,
    onStatsChange,
    savedPositions,
  ])

  if (isLoading) {
    return <GraphCanvasSkeleton />
  }

  if (!graph?.nodes?.length) {
    return <div className="flex h-full items-center justify-center text-[var(--text-muted)]">{t.common.notFound}</div>
  }

  return (
    <div className="graph-canvas-wrap relative h-full w-full">
      {showLegend ? <GraphLegendHelp /> : null}
      <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeDragStop={handlePersistPositions}
      onNodeClick={(_, node) => {
        window.clearTimeout(clickTimerRef.current)
        clickTimerRef.current = window.setTimeout(() => onOpenCi?.(Number(node.id)), 220)
      }}
      onNodeDoubleClick={(e, node) => {
        e.stopPropagation()
        window.clearTimeout(clickTimerRef.current)
        onSelectRoot?.(Number(node.id))
      }}
      onEdgesDelete={editable ? handleEdgesDelete : undefined}
      onConnect={handleConnect}
      onConnectStart={editable ? (_, { nodeId }) => {
        if (nodeId) window.clearTimeout(clickTimerRef.current)
      } : undefined}
      isValidConnection={isValidConnection}
      connectionMode={ConnectionMode.Loose}
      onEdgeClick={(_, edge) => {
        if (!editable || !edge.data) return
        const edgeData = edge.data as {
          relationId?: number
          sourceCiId?: number
          targetCiId?: number
          relationType?: string
          status?: string
          dataSource?: string
        }
        if (!edgeData.relationId || !edgeData.sourceCiId || !edgeData.targetCiId || !edgeData.relationType) return
        onEditRelationRequest?.({
          id: edgeData.relationId,
          sourceCiId: edgeData.sourceCiId,
          targetCiId: edgeData.targetCiId,
          relationType: edgeData.relationType,
          status: edgeData.status || 'active',
          dataSource: edgeData.dataSource || 'manual',
        })
      }}
      nodeTypes={graphNodeTypes}
      edgeTypes={graphEdgeTypes}
      minZoom={graphFlowDefaults.minZoom}
      maxZoom={graphFlowDefaults.maxZoom}
      panOnScroll={graphFlowDefaults.panOnScroll}
      zoomOnScroll={graphFlowDefaults.zoomOnScroll}
      zoomOnPinch={graphFlowDefaults.zoomOnPinch}
      zoomOnDoubleClick={graphFlowDefaults.zoomOnDoubleClick}
      selectNodesOnDrag={graphFlowDefaults.selectNodesOnDrag}
      nodesConnectable={editable}
      elementsSelectable={graphFlowDefaults.elementsSelectable}
      defaultEdgeOptions={graphFlowDefaults.defaultEdgeOptions}
      proOptions={{ hideAttribution: true }}
      className="graph-flow-canvas h-full w-full"
    >
      <Background color={gridColor} gap={32} size={0.75} />
      <Controls className="graph-controls" showInteractive={false} />
    </ReactFlow>
    </div>
  )
})

