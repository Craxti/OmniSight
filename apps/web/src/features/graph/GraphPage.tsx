import { ReactFlowProvider } from '@xyflow/react'
import { useRef } from 'react'
import { AutodiscoverModal } from '@/shared/components/autodiscover'
import { useI18n } from '@/context/useI18n'
import { PageHeader } from '@/components/ui'
import { DEFAULT_DATA_SOURCE, DEFAULT_RELATION_TYPE } from '@/shared/constants'
import { GraphCanvas, type GraphCanvasHandle, type GraphEdgeEditData } from '@/shared/components/graph/GraphCanvas'
import { GraphMapSidebar } from '@/features/graph/components/GraphMapSidebar'
import { GraphCreateRelationModal, GraphEditRelationModal } from '@/features/graph/components/GraphRelationModals'
import { useGraphPage, useGraphPageState } from '@/features/graph/hooks/useGraphPage'

export default function GraphPage() {
  const { t } = useI18n()
  const pageState = useGraphPageState()

  return (
    <div className="flex h-[calc(100vh-5rem)] min-h-[520px] flex-col gap-3">
      <PageHeader title={t.graph.title} subtitle={t.graph.subtitle} className="!mb-0 shrink-0" />
      <div className="card flex min-h-0 flex-1 overflow-hidden">
        <ReactFlowProvider>
          <GraphMapContent {...pageState} />
        </ReactFlowProvider>
      </div>
    </div>
  )
}

function GraphMapContent(props: ReturnType<typeof useGraphPageState>) {
  const { id, rootId, setRootId, depth, setDepth, relationFilter, setRelationFilter } = props
  const { t } = useI18n()
  const flowRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<GraphCanvasHandle>(null)
  const graphPage = useGraphPage({ ...props, flowRef, canvasRef })

  return (
    <div className="flex h-full min-h-0 flex-1">
      <GraphMapSidebar
        rootId={rootId}
        onRootChange={setRootId}
        depth={depth}
        onDepthChange={setDepth}
        relationFilter={relationFilter}
        onRelationFilterChange={setRelationFilter}
        nodeCount={graphPage.stats.nodes}
        edgeCount={graphPage.stats.edges}
        canExport={id > 0 && graphPage.stats.nodes > 0}
        onFit={() => canvasRef.current?.fit()}
        onRelayout={() => canvasRef.current?.relayout()}
        onExport={graphPage.exportGraph}
        businessPath={graphPage.businessPath?.path ?? []}
        impactedServices={graphPage.impact?.impacted_business_services ?? []}
        components={graphPage.components?.components ?? []}
        isBusinessServiceRoot={graphPage.isBusinessServiceRoot}
        validation={graphPage.validation ?? null}
        validating={graphPage.validating}
        onValidate={() => void graphPage.validateModel()}
        canEdit={graphPage.canEdit}
        onAutodiscover={() => graphPage.setAutodiscoverOpen(true)}
      />
      <div ref={flowRef} className="graph-flow-panel relative min-w-0 flex-1">
        {!id ? (
          <div className="flex h-full items-center justify-center p-6 text-center text-[var(--text-muted)]">
            {t.graph.empty}
          </div>
        ) : (
          <GraphCanvas
            ref={canvasRef}
            rootId={id}
            depth={depth}
            relationFilter={relationFilter}
            graph={graphPage.graph}
            pathIds={graphPage.pathIds}
            pathEdgeKeys={graphPage.pathEdgeKeys}
            impactIds={graphPage.impactIds}
            componentIds={graphPage.componentIds}
            isLoading={graphPage.isLoading}
            editable={graphPage.canEdit}
            onSelectRoot={(ciId) => setRootId(String(ciId))}
            onOpenCi={(ciId) => graphPage.navigate(`/inventory/${ciId}`)}
            onStatsChange={graphPage.setStats}
            onCreateRelationRequest={(sourceCiId, targetCiId) => {
              graphPage.setCreateDraft({ sourceCiId, targetCiId, relationType: DEFAULT_RELATION_TYPE, dataSource: DEFAULT_DATA_SOURCE })
            }}
            onEditRelationRequest={(edge: GraphEdgeEditData) => {
              graphPage.setEditDraft({
                id: edge.id,
                sourceCiId: edge.sourceCiId,
                targetCiId: edge.targetCiId,
                relationType: edge.relationType,
                status: edge.status,
                dataSource: edge.dataSource || DEFAULT_DATA_SOURCE,
              })
            }}
            onDeleteRelationRequest={(relationId) => graphPage.deleteRelationMut.mutate(relationId)}
          />
        )}
      </div>

      <GraphCreateRelationModal
        draft={graphPage.createDraft}
        onClose={() => graphPage.setCreateDraft(null)}
        onChange={graphPage.setCreateDraft}
        onSubmit={() => graphPage.createDraft && graphPage.createRelationMut.mutate(graphPage.createDraft)}
        pending={graphPage.createRelationMut.isPending}
        ciDisplay={graphPage.ciDisplay}
      />
      <GraphEditRelationModal
        draft={graphPage.editDraft}
        onClose={() => graphPage.setEditDraft(null)}
        onChange={graphPage.setEditDraft}
        onSubmit={() => graphPage.editDraft && graphPage.updateRelationMut.mutate(graphPage.editDraft)}
        onDelete={() => graphPage.editDraft && graphPage.deleteRelationMut.mutate(graphPage.editDraft.id)}
        updatePending={graphPage.updateRelationMut.isPending}
        deletePending={graphPage.deleteRelationMut.isPending}
        ciDisplay={graphPage.ciDisplay}
      />
      <AutodiscoverModal
        open={graphPage.autodiscoverOpen}
        onClose={() => graphPage.setAutodiscoverOpen(false)}
        scopeDefaults={{ scope_mode: 'graph', scope_depth: depth, root_ci_id: id > 0 ? id : undefined }}
        onApplied={() => {
          graphPage.invalidateGraph()
        }}
      />
    </div>
  )
}
