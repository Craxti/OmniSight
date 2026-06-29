export interface LayoutNode {
  id: number
  depth?: number
}

export interface LayoutEdge {
  source_ci_id: number
  target_ci_id: number
  relation_type?: string
}

export interface GraphLayoutResult {
  positions: Map<number, { x: number; y: number }>
  layers: Map<number, number>
}

const LAYER_HEIGHT = 168
const NODE_GAP = 240
const MARGIN_X = 80
const MARGIN_Y = 56
const FAN_MIN_CHILDREN = 3
const FAN_RADIUS = 300
const FAN_SPREAD = Math.PI * 0.82

/**
 * Vertical dependency layout: root at the bottom, graph neighbors above.
 * depends_on edge direction is always source -> target (dependent -> dependency).
 */
export function computeDependencyLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  rootId: number,
): Map<number, { x: number; y: number }> {
  return computeGraphLayout(nodes, edges, rootId).positions
}

export function computeGraphLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  rootId: number,
): GraphLayoutResult {
  const nodeIds = new Set(nodes.map((n) => n.id))
  const dependencies = new Map<number, number[]>()
  const adjacency = new Map<number, number[]>()

  for (const e of edges) {
    if (!nodeIds.has(e.source_ci_id) || !nodeIds.has(e.target_ci_id)) continue
    adjacency.set(e.source_ci_id, [...(adjacency.get(e.source_ci_id) ?? []), e.target_ci_id])
    adjacency.set(e.target_ci_id, [...(adjacency.get(e.target_ci_id) ?? []), e.source_ci_id])
    if (!e.relation_type || e.relation_type === 'depends_on') {
      dependencies.set(e.source_ci_id, [...(dependencies.get(e.source_ci_id) ?? []), e.target_ci_id])
    }
  }

  const layer = new Map<number, number>()
  if (nodeIds.has(rootId)) {
    const queue: number[] = [rootId]
    layer.set(rootId, 0)
    while (queue.length) {
      const id = queue.shift()!
      for (const next of adjacency.get(id) ?? []) {
        if (!layer.has(next)) {
          layer.set(next, (layer.get(id) ?? 0) + 1)
          queue.push(next)
        }
      }
    }
  }

  for (const n of nodes) {
    if (!layer.has(n.id)) layer.set(n.id, (n.depth ?? 0) + 1)
  }

  const byLayer = new Map<number, number[]>()
  for (const n of nodes) {
    const l = layer.get(n.id) ?? 0
    if (!byLayer.has(l)) byLayer.set(l, [])
    byLayer.get(l)!.push(n.id)
  }

  const sortedLayers = [...byLayer.keys()].sort((a, b) => a - b)
  const maxLayer = sortedLayers.at(-1) ?? 0

  for (let i = 1; i < sortedLayers.length; i++) {
    const l = sortedLayers[i]
    const below = sortedLayers[i - 1]
    const belowOrder = new Map((byLayer.get(below) ?? []).map((id, idx) => [id, idx]))
    const list = [...(byLayer.get(l) ?? [])]
    list.sort((a, b) => {
      const scoreA = avgIndex(a, dependencies, belowOrder)
      const scoreB = avgIndex(b, dependencies, belowOrder)
      return scoreA - scoreB || a - b
    })
    byLayer.set(l, list)
  }

  const positions = new Map<number, { x: number; y: number }>()
  const maxRow = Math.max(...[...byLayer.values()].map((row) => row.length), 1)

  for (const [l, ids] of byLayer) {
    const rowWidth = (ids.length - 1) * NODE_GAP
    const centerX = MARGIN_X + ((maxRow - 1) * NODE_GAP) / 2
    const startX = centerX - rowWidth / 2
    const y = MARGIN_Y + (maxLayer - l) * LAYER_HEIGHT
    ids.forEach((id, i) => {
      positions.set(id, { x: startX + i * NODE_GAP, y })
    })
  }

  applyRadialFan(positions, layer, adjacency)

  return { positions, layers: layer }
}

function applyRadialFan(
  positions: Map<number, { x: number; y: number }>,
  layer: Map<number, number>,
  adjacency: Map<number, number[]>,
): void {
  const childrenByParent = new Map<number, number[]>()

  for (const [nodeId, neighbors] of adjacency) {
    const nodeLayer = layer.get(nodeId) ?? 0
    for (const neighbor of neighbors) {
      const neighborLayer = layer.get(neighbor) ?? 0
      if (neighborLayer <= nodeLayer) continue
      const parent = nodeId
      const child = neighbor
      const list = childrenByParent.get(parent) ?? []
      if (!list.includes(child)) list.push(child)
      childrenByParent.set(parent, list)
    }
  }

  for (const [parentId, children] of childrenByParent) {
    if (children.length < FAN_MIN_CHILDREN) continue
    const parentPos = positions.get(parentId)
    if (!parentPos) continue

    const count = children.length
    const startAngle = -Math.PI / 2 - FAN_SPREAD / 2
    const step = count > 1 ? FAN_SPREAD / (count - 1) : 0

    children.forEach((childId, i) => {
      const angle = startAngle + step * i
      positions.set(childId, {
        x: parentPos.x + FAN_RADIUS * Math.cos(angle),
        y: parentPos.y + FAN_RADIUS * Math.sin(angle),
      })
    })
  }
}

function avgIndex(
  nodeId: number,
  dependencies: Map<number, number[]>,
  belowOrder: Map<number, number>,
): number {
  const targets = (dependencies.get(nodeId) ?? []).filter((t) => belowOrder.has(t))
  if (!targets.length) return Number.POSITIVE_INFINITY
  return targets.reduce((sum, t) => sum + (belowOrder.get(t) ?? 0), 0) / targets.length
}

/** @deprecated use computeDependencyLayout */
export function computeNodePositions(
  nodes: LayoutNode[],
  edges: LayoutEdge[] = [],
  rootId?: number,
): Map<number, { x: number; y: number }> {
  if (rootId) return computeDependencyLayout(nodes, edges, rootId)
  return computeDependencyLayout(nodes, edges, nodes[0]?.id ?? 0)
}

export const graphFlowDefaults = {
  minZoom: 0.4,
  maxZoom: 2.5,
  panOnScroll: false,
  zoomOnScroll: true,
  zoomOnPinch: true,
  zoomOnDoubleClick: false,
  selectNodesOnDrag: false,
  nodesConnectable: false,
  elementsSelectable: true,
  fitViewOptions: { padding: 0.2, duration: 550 },
  defaultEdgeOptions: {
    type: 'smoothstep' as const,
    style: { strokeWidth: 2 },
  },
}
