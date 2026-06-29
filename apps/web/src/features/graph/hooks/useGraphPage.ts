import { toPng } from 'html-to-image'
import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { useTheme } from '@/context/useTheme'
import { useToast } from '@/context/useToast'
import {
  type RelationCreateDraft,
  type RelationEditDraft,
} from '@/shared/hooks/useRelationDraftMutations'
import { useRelationValidation } from '@/shared/hooks/useRelationValidation'
import type { GraphCanvasHandle } from '@/shared/components/graph/GraphCanvas'
import { useGraphQueries } from '@/features/graph/hooks/useGraphQueries'
import { useGraphRelationActions } from '@/features/graph/hooks/useGraphRelationActions'

export type { RelationCreateDraft, RelationEditDraft } from '@/shared/hooks/useRelationDraftMutations'

export function useGraphPageState() {
  const [params, setParams] = useSearchParams()
  const [rootId, setRootId] = useState(params.get('root') || '')
  const [depth, setDepth] = useState(3)
  const [relationFilter, setRelationFilter] = useState('')
  const id = Number(rootId)

  return { params, setParams, rootId, setRootId, depth, setDepth, relationFilter, setRelationFilter, id }
}

export function useGraphPage({
  id,
  depth,
  rootId,
  relationFilter,
  setRelationFilter,
  params,
  setParams,
}: ReturnType<typeof useGraphPageState>) {
  const { t } = useI18n()
  const { theme } = useTheme()
  const { success, error: toastError } = useToast()
  const { canEdit } = useAuth()
  const navigate = useNavigate()
  const flowRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<GraphCanvasHandle>(null)
  const [stats, setStats] = useState({ nodes: 0, edges: 0 })
  const [createDraft, setCreateDraft] = useState<RelationCreateDraft | null>(null)
  const [editDraft, setEditDraft] = useState<RelationEditDraft | null>(null)
  const [autodiscoverOpen, setAutodiscoverOpen] = useState(false)

  const queries = useGraphQueries(id, depth)
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
    if (!rootId) return
    if (params.get('root') === rootId) return
    setParams({ root: rootId }, { replace: true })
  }, [rootId, params, setParams])

  const exportGraph = async () => {
    if (!flowRef.current) return
    try {
      const exportBg = theme === 'light' ? '#f4f6f9' : '#111827'
      const dataUrl = await toPng(flowRef.current, { backgroundColor: exportBg, pixelRatio: 2 })
      const link = document.createElement('a')
      link.download = `omnisight-graph-${id}.png`
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
    flowRef,
    canvasRef,
    stats,
    setStats,
    createDraft,
    setCreateDraft,
    editDraft,
    setEditDraft,
    autodiscoverOpen,
    setAutodiscoverOpen,
    ...queries,
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
