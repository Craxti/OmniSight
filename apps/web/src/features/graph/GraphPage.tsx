import { ReactFlowProvider } from '@xyflow/react'
import { AutodiscoverModal } from '@/shared/components/autodiscover'
import { useI18n } from '@/context/useI18n'
import { PageHeader } from '@/components/ui'
import { DEFAULT_DATA_SOURCE, DEFAULT_RELATION_TYPE } from '@/shared/constants'
import { GraphCanvas, type GraphEdgeEditData } from '@/shared/components/graph/GraphCanvas'
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
  const graph = useGraphPage(props)

  return (
    <div className="flex h-full min-h-0 flex-1">
      <GraphMapSidebar
        rootId={rootId}
        onRootChange={setRootId}
        depth={depth}
        onDepthChange={setDepth}
        relationFilter={relationFilter}
        onRelationFilterChange={setRelationFilter}
        nodeCount={graph.stats.nodes}
        edgeCount={graph.stats.edges}
        canExport={id > 0 && graph.stats.nodes > 0}
        onFit={() => graph.canvasRef.current?.fit()}
        onRelayout={() => graph.canvasRef.current?.relayout()}
        onExport={graph.exportGraph}
        businessPath={graph.businessPath?.path ?? []}
        impactedServices={graph.impact?.impacted_business_services ?? []}
        components={graph.components?.components ?? []}
        isBusinessServiceRoot={graph.isBusinessServiceRoot}
        validation={graph.validation ?? null}
        validating={graph.validating}
        onValidate={() => void graph.validateModel()}
        canEdit={graph.canEdit}
        onAutodiscover={() => graph.setAutodiscoverOpen(true)}
      />
      <div ref={graph.flowRef} className="graph-flow-panel relative min-w-0 flex-1">
        {!id ? (
          <div className="flex h-full items-center justify-center p-6 text-center text-[var(--text-muted)]">
            {t.graph.empty}
          </div>
        ) : (
          <GraphCanvas
            ref={graph.canvasRef}
            rootId={id}
            depth={depth}
            relationFilter={relationFilter}
            graph={graph.graph}
            pathIds={graph.pathIds}
            pathEdgeKeys={graph.pathEdgeKeys}
            impactIds={graph.impactIds}
            componentIds={graph.componentIds}
            isLoading={graph.isLoading}
            editable={graph.canEdit}
            onSelectRoot={(ciId) => setRootId(String(ciId))}
            onOpenCi={(ciId) => graph.navigate(`/inventory/${ciId}`)}
            onStatsChange={graph.setStats}
            onCreateRelationRequest={(sourceCiId, targetCiId) => {
              graph.setCreateDraft({ sourceCiId, targetCiId, relationType: DEFAULT_RELATION_TYPE, dataSource: DEFAULT_DATA_SOURCE })
            }}
            onEditRelationRequest={(edge: GraphEdgeEditData) => {
              graph.setEditDraft({
                id: edge.id,
                sourceCiId: edge.sourceCiId,
                targetCiId: edge.targetCiId,
                relationType: edge.relationType,
                status: edge.status,
                dataSource: edge.dataSource || DEFAULT_DATA_SOURCE,
              })
            }}
            onDeleteRelationRequest={(relationId) => graph.deleteRelationMut.mutate(relationId)}
          />
        )}
      </div>

      <GraphCreateRelationModal
        draft={graph.createDraft}
        onClose={() => graph.setCreateDraft(null)}
        onChange={graph.setCreateDraft}
        onSubmit={() => graph.createDraft && graph.createRelationMut.mutate(graph.createDraft)}
        pending={graph.createRelationMut.isPending}
        ciDisplay={graph.ciDisplay}
      />
      <GraphEditRelationModal
        draft={graph.editDraft}
        onClose={() => graph.setEditDraft(null)}
        onChange={graph.setEditDraft}
        onSubmit={() => graph.editDraft && graph.updateRelationMut.mutate(graph.editDraft)}
        onDelete={() => graph.editDraft && graph.deleteRelationMut.mutate(graph.editDraft.id)}
        updatePending={graph.updateRelationMut.isPending}
        deletePending={graph.deleteRelationMut.isPending}
        ciDisplay={graph.ciDisplay}
      />
      <AutodiscoverModal
        open={graph.autodiscoverOpen}
        onClose={() => graph.setAutodiscoverOpen(false)}
        scopeDefaults={{ scope_mode: 'graph', scope_depth: depth, root_ci_id: id > 0 ? id : undefined }}
        onApplied={() => {
          graph.invalidateGraph()
        }}
      />
    </div>
  )
}
