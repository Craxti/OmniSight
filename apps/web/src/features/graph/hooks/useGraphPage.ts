import { toPng } from 'html-to-image'
import { useEffect, useMemo, useState, type RefObject } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { useToast } from '@/context/useToast'
import {
  type RelationCreateDraft,
  type RelationEditDraft,
} from '@/shared/hooks/useRelationDraftMutations'
import { useRelationValidation } from '@/shared/hooks/useRelationValidation'
import type { GraphCanvasHandle } from '@/shared/components/graph/GraphCanvas'
import { useGraphOverview } from '@/features/graph/hooks/useGraphOverview'
import { useGraphQueries } from '@/features/graph/hooks/useGraphQueries'
import { useGraphRelationActions } from '@/features/graph/hooks/useGraphRelationActions'

export type { RelationCreateDraft, RelationEditDraft } from '@/shared/hooks/useRelationDraftMutations'

export function useGraphPageState() {
  const [params, setParams] = useSearchParams()
  const [rootId, setRootId] = useState(params.get('root') || '')
  const [depth, setDepth] = useState(3)
  const [relationFilter, setRelationFilter] = useState('')
  const id = Number(rootId)
  const isOverview = !rootId

  return {
    params,
    setParams,
    rootId,
    setRootId,
    depth,
    setDepth,
    relationFilter,
    setRelationFilter,
    id,
    isOverview,
  }
}

export type GraphPageRefs = {
  flowRef: RefObject<HTMLDivElement | null>
  canvasRef: RefObject<GraphCanvasHandle | null>
}

export function useGraphPage({
  id,
  depth,
  rootId,
  isOverview,
  relationFilter,
  setRelationFilter,
  params,
  setParams,
  flowRef,
}: ReturnType<typeof useGraphPageState> & GraphPageRefs) {
  const { t } = useI18n()
  const { success, error: toastError } = useToast()
  const { canEdit } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState({ nodes: 0, edges: 0 })
  const [createDraft, setCreateDraft] = useState<RelationCreateDraft | null>(null)
  const [editDraft, setEditDraft] = useState<RelationEditDraft | null>(null)
  const [autodiscoverOpen, setAutodiscoverOpen] = useState(false)

  const focusedQueries = useGraphQueries(id, depth)
  const overviewQueries = useGraphOverview(isOverview)
  const emptyIds = useMemo(() => new Set<number>(), [])
  const emptyKeys = useMemo(() => new Set<string>(), [])

  const { validation, validate: validateModel, validating } = useRelationValidation()

  const { invalidateGraph, createRelationMut, updateRelationMut, deleteRelationMut } =
    useGraphRelationActions({
      rootId: id,
      depth,
      relationFilter,
      setRelationFilter,
      onCreateSuccess: () => setCreateDraft(null),
      onEditSuccess: () => setEditDraft(null),
    })

  useEffect(() => {
    if (rootId) {
      if (params.get('root') === rootId) return
      setParams({ root: rootId }, { replace: true })
      return
    }
    if (params.has('root')) {
      setParams({}, { replace: true })
    }
  }, [rootId, params, setParams])

  const exportGraph = async () => {
    if (!flowRef.current) return
    try {
      const exportBg = getComputedStyle(document.documentElement).getPropertyValue('--graph-export-bg').trim()
      const dataUrl = await toPng(flowRef.current, { backgroundColor: exportBg, pixelRatio: 2 })
      const link = document.createElement('a')
      link.download = isOverview ? 'omnisight-graph-overview.png' : `omnisight-graph-${id}.png`
      link.href = dataUrl
      link.click()
      success(t.graph.toastExported)
    } catch {
      toastError(t.graph.toastExportError)
    }
  }

  return {
    t,
    canEdit,
    navigate,
    stats,
    setStats,
    createDraft,
    setCreateDraft,
    editDraft,
    setEditDraft,
    autodiscoverOpen,
    setAutodiscoverOpen,
    graph: isOverview ? overviewQueries.graph : focusedQueries.graph,
    isLoading: isOverview ? overviewQueries.isLoading : focusedQueries.isLoading,
    ciDisplay: isOverview ? overviewQueries.ciDisplay : focusedQueries.ciDisplay,
    businessPath: isOverview ? undefined : focusedQueries.businessPath,
    impact: isOverview ? undefined : focusedQueries.impact,
    components: isOverview ? undefined : focusedQueries.components,
    pathIds: isOverview ? emptyIds : focusedQueries.pathIds,
    pathEdgeKeys: isOverview ? emptyKeys : focusedQueries.pathEdgeKeys,
    impactIds: isOverview ? emptyIds : focusedQueries.impactIds,
    componentIds: isOverview ? emptyIds : focusedQueries.componentIds,
    isBusinessServiceRoot: isOverview ? false : focusedQueries.isBusinessServiceRoot,
    isOverview,
    validation,
    validating,
    validateModel,
    exportGraph,
    invalidateGraph,
    createRelationMut,
    updateRelationMut,
    deleteRelationMut,
  }
}
