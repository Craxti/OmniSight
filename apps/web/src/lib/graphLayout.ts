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

const LAYER_HEIGHT = 200
const NODE_GAP = 280
const MARGIN_X = 120
const MARGIN_Y = 72
const BARYCENTER_PASSES = 6
const MIN_NODE_GAP = 240
const DEP_OFFSET = 300

/**
 * Vertical layout: root at the bottom, BFS neighbors above.
 * depends_on edge direction is always source -> target (dependent -> dependency).
 */
export function computeDependencyLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  rootId: number,
): Map<number, { x: number; y: number }> {
  return computeGraphLayout(nodes, edges, rootId).positions
}

const RADIAL_RING_GAP = 220
const RADIAL_COMPONENT_GAP = 520

export function computeGraphLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
  rootId: number,
): GraphLayoutResult {
  const nodeIds = new Set(nodes.map((n) => n.id))
  const { adjacency, dependencies, dependents } = buildGraphMaps(nodes, edges, nodeIds)

  if (!rootId || !nodeIds.has(rootId)) {
    return computeCircularOverviewLayout(nodes, edges)
  }

  const layer = computeLayers(nodes, adjacency, rootId)
  return layoutFromLayers(nodes, layer, adjacency, dependencies, dependents, rootId)
}

/** Radial layout for the full model map when no root CI is selected. */
export function computeOverviewLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
): GraphLayoutResult {
  return computeCircularOverviewLayout(nodes, edges)
}

function computeCircularOverviewLayout(
  nodes: LayoutNode[],
  edges: LayoutEdge[],
): GraphLayoutResult {
  if (!nodes.length) return { positions: new Map(), layers: new Map() }

  const nodeIds = new Set(nodes.map((n) => n.id))
  const { adjacency } = buildGraphMaps(nodes, edges, nodeIds)
  const components = findConnectedComponents(nodes, adjacency)
  const positions = new Map<number, { x: number; y: number }>()
  const layers = new Map<number, number>()

  let offsetX = 0

  for (const component of components) {
    const componentSet = new Set(component)
    const hubId = pickLayoutHub(component, adjacency)
    const rings = bfsRings(hubId, componentSet, adjacency)
    const byRing = groupIdsByRing(rings)
    const maxRing = Math.max(...byRing.keys(), 0)
    const outerRadius = ringRadius(maxRing, byRing.get(maxRing)?.length ?? 1)
    const cx = MARGIN_X + offsetX + outerRadius
    const cy = MARGIN_Y + outerRadius

    for (const [ring, ids] of byRing) {
      const sorted = [...ids].sort((a, b) => a - b)
      layers.set(hubId, 0)
      for (const id of sorted) layers.set(id, ring)

      if (ring === 0) {
        positions.set(hubId, { x: cx, y: cy })
        continue
      }

      const radius = ringRadius(ring, sorted.length)
      sorted.forEach((id, index) => {
        const angle = (2 * Math.PI * index) / sorted.length - Math.PI / 2
        positions.set(id, {
          x: cx + radius * Math.cos(angle),
          y: cy + radius * Math.sin(angle),
        })
      })
    }

    offsetX += outerRadius * 2 + RADIAL_COMPONENT_GAP
  }

  centerLayout(positions)
  return { positions, layers }
}

function findConnectedComponents(
  nodes: LayoutNode[],
  adjacency: Map<number, number[]>,
): number[][] {
  const visited = new Set<number>()
  const components: number[][] = []

  for (const n of nodes) {
    if (visited.has(n.id)) continue
    const stack = [n.id]
    const component: number[] = []
    visited.add(n.id)
    while (stack.length) {
      const id = stack.pop()!
      component.push(id)
      for (const next of adjacency.get(id) ?? []) {
        if (visited.has(next)) continue
        visited.add(next)
        stack.push(next)
      }
    }
    components.push(component)
  }

  return components
}

function pickLayoutHub(component: number[], adjacency: Map<number, number[]>): number {
  return component.reduce((best, id) => {
    const degree = adjacency.get(id)?.length ?? 0
    const bestDegree = adjacency.get(best)?.length ?? -1
    return degree > bestDegree || (degree === bestDegree && id < best) ? id : best
  })
}

function bfsRings(
  start: number,
  component: Set<number>,
  adjacency: Map<number, number[]>,
): Map<number, number> {
  const rings = new Map<number, number>()
  const queue: number[] = [start]
  rings.set(start, 0)

  while (queue.length) {
    const id = queue.shift()!
    for (const next of adjacency.get(id) ?? []) {
      if (!component.has(next) || rings.has(next)) continue
      rings.set(next, rings.get(id)! + 1)
      queue.push(next)
    }
  }

  for (const id of component) {
    if (!rings.has(id)) rings.set(id, 1)
  }

  return rings
}

function groupIdsByRing(rings: Map<number, number>): Map<number, number[]> {
  const byRing = new Map<number, number[]>()
  for (const [id, ring] of rings) {
    if (!byRing.has(ring)) byRing.set(ring, [])
    byRing.get(ring)!.push(id)
  }
  return byRing
}

function ringRadius(ring: number, nodeCount: number): number {
  if (ring <= 0) return 0
  const spreadRadius = nodeCount <= 1 ? RADIAL_RING_GAP : (nodeCount * MIN_NODE_GAP) / (2 * Math.PI)
  return Math.max(ring * RADIAL_RING_GAP, spreadRadius)
}

function centerLayout(positions: Map<number, { x: number; y: number }>): void {
  const coords = [...positions.values()]
  if (!coords.length) return

  const minX = Math.min(...coords.map((p) => p.x))
  const minY = Math.min(...coords.map((p) => p.y))
  const shiftX = MARGIN_X - minX
  const shiftY = MARGIN_Y - minY

  for (const [id, pos] of positions) {
    positions.set(id, { x: pos.x + shiftX, y: pos.y + shiftY })
  }
}

function buildGraphMaps(
  _nodes: LayoutNode[],
  edges: LayoutEdge[],
  nodeIds: Set<number>,
): {
  adjacency: Map<number, number[]>
  dependencies: Map<number, number[]>
  dependents: Map<number, number[]>
} {
  const adjacency = new Map<number, number[]>()
  const dependencies = new Map<number, number[]>()
  const dependents = new Map<number, number[]>()

  for (const e of edges) {
    if (!nodeIds.has(e.source_ci_id) || !nodeIds.has(e.target_ci_id)) continue
    adjacency.set(e.source_ci_id, [...(adjacency.get(e.source_ci_id) ?? []), e.target_ci_id])
    adjacency.set(e.target_ci_id, [...(adjacency.get(e.target_ci_id) ?? []), e.source_ci_id])
    if (!e.relation_type || e.relation_type === 'depends_on') {
      dependencies.set(e.source_ci_id, [...(dependencies.get(e.source_ci_id) ?? []), e.target_ci_id])
      dependents.set(e.target_ci_id, [...(dependents.get(e.target_ci_id) ?? []), e.source_ci_id])
    }
  }

  return { adjacency, dependencies, dependents }
}

function layoutFromLayers(
  nodes: LayoutNode[],
  layer: Map<number, number>,
  adjacency: Map<number, number[]>,
  dependencies: Map<number, number[]>,
  dependents: Map<number, number[]>,
  rootId: number | null,
): GraphLayoutResult {
  const maxLayer = Math.max(...[...layer.values()], 0)
  const byLayer = groupByLayer(nodes, layer)
  const sortedLayers = [...byLayer.keys()].sort((a, b) => a - b)

  const spineIds = new Set<number>()
  if (rootId != null) {
    const dependentChain = walkDependsOnChain(rootId, (id) => dependents.get(id) ?? [])
    const dependencyChain = walkDependsOnChain(rootId, (id) => dependencies.get(id) ?? [])
    for (const id of [...dependentChain, ...dependencyChain]) spineIds.add(id)
  }

  const order = new Map<number, number>()
  for (const ids of byLayer.values()) {
    ids.forEach((id, index) => order.set(id, index))
  }

  for (let pass = 0; pass < BARYCENTER_PASSES; pass++) {
    for (let i = 1; i < sortedLayers.length; i++) {
      const l = sortedLayers[i]!
      const below = sortedLayers[i - 1]!
      const belowOrder = layerIndexMap(byLayer.get(below) ?? [], order)
      byLayer.set(
        l,
        sortLayerIds(byLayer.get(l) ?? [], belowOrder, adjacency, (id) => layer.get(id) === below),
      )
      syncOrder(byLayer.get(l) ?? [], order)
    }

    for (let i = sortedLayers.length - 2; i >= 0; i--) {
      const l = sortedLayers[i]!
      const above = sortedLayers[i + 1]!
      const aboveOrder = layerIndexMap(byLayer.get(above) ?? [], order)
      byLayer.set(
        l,
        sortLayerIds(byLayer.get(l) ?? [], aboveOrder, adjacency, (id) => layer.get(id) === above),
      )
      syncOrder(byLayer.get(l) ?? [], order)
    }
  }

  if (spineIds.size) pinSpineOrder(byLayer, sortedLayers, spineIds, order)

  const maxRow = Math.max(...[...byLayer.values()].map((row) => row.length), 1)
  const positions = new Map<number, { x: number; y: number }>()

  for (const l of sortedLayers) {
    const ids = byLayer.get(l) ?? []
    const rowWidth = Math.max(0, ids.length - 1) * NODE_GAP
    const centerX = MARGIN_X + ((maxRow - 1) * NODE_GAP) / 2
    const startX = centerX - rowWidth / 2
    const y = layerY(l, maxLayer)

    ids.forEach((id, index) => {
      positions.set(id, { x: startX + index * NODE_GAP, y })
    })
  }

  if (rootId != null) {
    const dependentChain = walkDependsOnChain(rootId, (id) => dependents.get(id) ?? [])
    const dependencyChain = walkDependsOnChain(rootId, (id) => dependencies.get(id) ?? [])
    alignSpineColumn(positions, dependentChain, dependencyChain, rootId)
  }

  resolveLayerCollisions(positions, layer, spineIds)
  centerHorizontally(positions)

  return { positions, layers: layer }
}

function layerY(layerIndex: number, maxLayer: number): number {
  return MARGIN_Y + (maxLayer - layerIndex) * LAYER_HEIGHT
}

function computeLayers(
  nodes: LayoutNode[],
  adjacency: Map<number, number[]>,
  rootId: number,
): Map<number, number> {
  const nodeIds = new Set(nodes.map((n) => n.id))
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

  return layer
}

function groupByLayer(nodes: LayoutNode[], layer: Map<number, number>): Map<number, number[]> {
  const byLayer = new Map<number, number[]>()
  for (const n of nodes) {
    const l = layer.get(n.id) ?? 0
    if (!byLayer.has(l)) byLayer.set(l, [])
    byLayer.get(l)!.push(n.id)
  }
  return byLayer
}

function layerIndexMap(ids: number[], order: Map<number, number>): Map<number, number> {
  return new Map(ids.map((id, index) => [id, order.get(id) ?? index]))
}

function syncOrder(ids: number[], order: Map<number, number>): void {
  ids.forEach((id, index) => order.set(id, index))
}

function sortLayerIds(
  ids: number[],
  referenceOrder: Map<number, number>,
  adjacency: Map<number, number[]>,
  isReferenceNeighbor: (neighborId: number) => boolean,
): number[] {
  return [...ids].sort((a, b) => {
    const scoreA = avgNeighborOrder(a, referenceOrder, adjacency, isReferenceNeighbor)
    const scoreB = avgNeighborOrder(b, referenceOrder, adjacency, isReferenceNeighbor)
    return scoreA - scoreB || a - b
  })
}

function avgNeighborOrder(
  nodeId: number,
  referenceOrder: Map<number, number>,
  adjacency: Map<number, number[]>,
  isReferenceNeighbor: (neighborId: number) => boolean,
): number {
  const refs = (adjacency.get(nodeId) ?? []).filter(isReferenceNeighbor)
  const scored = refs
    .map((id) => referenceOrder.get(id))
    .filter((value): value is number => value !== undefined)
  if (!scored.length) return Number.POSITIVE_INFINITY
  return scored.reduce((sum, value) => sum + value, 0) / scored.length
}

function walkDependsOnChain(start: number, nextOf: (id: number) => number[]): number[] {
  const chain = [start]
  const seen = new Set<number>([start])
  let current = start

  while (true) {
    const candidates = nextOf(current).filter((id) => !seen.has(id))
    if (candidates.length !== 1) break
    const next = candidates[0]!
    chain.push(next)
    seen.add(next)
    current = next
  }

  return chain
}

function pinSpineOrder(
  byLayer: Map<number, number[]>,
  sortedLayers: number[],
  spineIds: Set<number>,
  order: Map<number, number>,
): void {
  for (const l of sortedLayers) {
    const ids = byLayer.get(l) ?? []
    const spine = ids.filter((id) => spineIds.has(id))
    if (!spine.length) continue

    const others = ids.filter((id) => !spineIds.has(id))
    const left = others.filter((id) => (order.get(id) ?? 0) < (order.get(spine[0]!) ?? 0))
    const right = others.filter((id) => (order.get(id) ?? 0) >= (order.get(spine[0]!) ?? 0))
    const next = [...left, ...spine, ...right]
    byLayer.set(l, next)
    syncOrder(next, order)
  }
}

function alignSpineColumn(
  positions: Map<number, { x: number; y: number }>,
  dependentChain: number[],
  dependencyChain: number[],
  rootId: number,
): void {
  const rootPos = positions.get(rootId)
  if (!rootPos) return

  for (const id of dependentChain) {
    const pos = positions.get(id)
    if (!pos) continue
    positions.set(id, { x: rootPos.x, y: pos.y })
  }

  for (const id of dependencyChain) {
    if (id === rootId) continue
    const pos = positions.get(id)
    if (!pos) continue
    positions.set(id, { x: rootPos.x - DEP_OFFSET, y: pos.y })
  }
}

function resolveLayerCollisions(
  positions: Map<number, { x: number; y: number }>,
  layer: Map<number, number>,
  spineIds: Set<number>,
): void {
  const byLayer = new Map<number, number[]>()
  for (const [id] of positions) {
    const l = layer.get(id) ?? 0
    if (!byLayer.has(l)) byLayer.set(l, [])
    byLayer.get(l)!.push(id)
  }

  for (const ids of byLayer.values()) {
    const sorted = [...ids].sort((a, b) => (positions.get(a)?.x ?? 0) - (positions.get(b)?.x ?? 0))

    for (let i = 1; i < sorted.length; i++) {
      const prev = sorted[i - 1]!
      const cur = sorted[i]!
      const prevPos = positions.get(prev)!
      const curPos = positions.get(cur)!
      const overlap = prevPos.x + MIN_NODE_GAP - curPos.x
      if (overlap <= 0) continue

      if (spineIds.has(cur) && !spineIds.has(prev)) {
        positions.set(prev, { x: prevPos.x - overlap, y: prevPos.y })
      } else {
        positions.set(cur, { x: curPos.x + overlap, y: curPos.y })
      }
    }
  }
}

function centerHorizontally(positions: Map<number, { x: number; y: number }>): void {
  const xs = [...positions.values()].map((p) => p.x)
  if (!xs.length) return
  const minX = Math.min(...xs)
  if (minX === MARGIN_X) return
  const shift = MARGIN_X - minX
  for (const [id, pos] of positions) {
    positions.set(id, { x: pos.x + shift, y: pos.y })
  }
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
