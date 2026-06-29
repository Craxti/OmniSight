import { Modal, Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { RelationFormFields } from '@/shared/components/RelationFormFields'
import type { RelationCreateDraft, RelationEditDraft } from '@/features/graph/hooks/useGraphPage'

type CreateProps = {
  draft: RelationCreateDraft | null
  onClose: () => void
  onChange: (draft: RelationCreateDraft) => void
  onSubmit: () => void
  pending: boolean
  ciDisplay: (ciId: number) => string
}

export function GraphCreateRelationModal({ draft, onClose, onChange, onSubmit, pending, ciDisplay }: CreateProps) {
  const { t } = useI18n()
  return (
    <Modal open={draft !== null} onClose={onClose} title={t.graph.newRelationTitle}>
      {draft && (
        <>
          <div className="space-y-3">
            <div className="text-sm text-[var(--text-muted)]">{t.graph.newRelationHint}</div>
            <RelationFormFields
              mode="readonly"
              sourceCiId={draft.sourceCiId}
              targetCiId={draft.targetCiId}
              ciDisplay={ciDisplay}
              relationType={draft.relationType}
              dataSource={draft.dataSource}
              onRelationTypeChange={(relationType) => onChange({ ...draft, relationType })}
              onDataSourceChange={(dataSource) => onChange({ ...draft, dataSource })}
            />
          </div>
          <FormModalActions
            onCancel={onClose}
            onSubmit={onSubmit}
            submitLabel={t.common.create}
            pending={pending}
          />
        </>
      )}
    </Modal>
  )
}

type EditProps = {
  draft: RelationEditDraft | null
  onClose: () => void
  onChange: (draft: RelationEditDraft) => void
  onSubmit: () => void
  onDelete: () => void
  updatePending: boolean
  deletePending: boolean
  ciDisplay: (ciId: number) => string
}

export function GraphEditRelationModal({
  draft,
  onClose,
  onChange,
  onSubmit,
  onDelete,
  updatePending,
  deletePending,
  ciDisplay,
}: EditProps) {
  const { t } = useI18n()
  return (
    <Modal open={draft !== null} onClose={onClose} title={t.graph.editRelationTitle}>
      {draft && (
        <>
          <div className="space-y-3">
            <div className="text-sm text-[var(--text-muted)]">{t.graph.editRelationHint}</div>
            <RelationFormFields
              mode="edit-with-endpoints"
              sourceCiId={draft.sourceCiId}
              targetCiId={draft.targetCiId}
              ciDisplay={ciDisplay}
              relationType={draft.relationType}
              status={draft.status}
              dataSource={draft.dataSource}
              onRelationTypeChange={(relationType) => onChange({ ...draft, relationType })}
              onStatusChange={(status) => onChange({ ...draft, status })}
              onDataSourceChange={(dataSource) => onChange({ ...draft, dataSource })}
            />
          </div>
          <FormModalActions
            layout="destructive"
            destructiveAction={
              <Button
                variant="danger"
                onClick={onDelete}
                disabled={deletePending || updatePending}
                data-testid="graph-relation-delete"
              >
                {t.graph.deleteRelation}
              </Button>
            }
            onCancel={onClose}
            onSubmit={onSubmit}
            submitLabel={t.common.save}
            pending={updatePending || deletePending}
          />
        </>
      )}
    </Modal>
  )
}
