import { GitBranch, Pencil, Plus, Trash2 } from 'lucide-react'
import { Button, EmptyState, CardGridSkeleton } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { relationTypeLabel } from '@/lib/domainLabels'
import { isRelationTypeProtected } from '@/lib/relationTypeCatalog'
import type { RelationType } from '@/shared/api/v1Inventory'
import { useRelationTypes } from '@/shared/hooks/useRelationTypes'
import { SectionHead } from '@/features/settings/components/SettingsUi'

type Props = {
  isAdmin: boolean
  onNewType: () => void
  onEditType: (relationType: RelationType) => void
  onDeleteType: (id: number) => void
}

function RelationTypeCard({
  relationType,
  isAdmin,
  onEdit,
  onDelete,
}: {
  relationType: RelationType
  isAdmin: boolean
  onEdit: () => void
  onDelete: () => void
}) {
  const { t } = useI18n()
  const isBuiltin = isRelationTypeProtected(relationType)
  const title = isBuiltin
    ? relationTypeLabel(t, relationType.name)
    : relationTypeLabel(t, relationType.name, relationType.description)

  return (
    <div className="group card-hover-brand rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-hover)] p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="font-medium text-[var(--text-primary)]">{title}</div>
          <div className="mt-1 flex flex-wrap items-center gap-1.5 font-mono text-xs text-[var(--text-muted)]">
            <span>{relationType.name}</span>
            {isBuiltin && <span className="badge badge-indigo font-sans">{t.settings.official}</span>}
          </div>
          {!isBuiltin && relationType.description && (
            <p className="mt-2 line-clamp-2 text-xs text-[var(--text-muted)]">{relationType.description}</p>
          )}
        </div>
        {isAdmin && !isBuiltin && (
          <div className="flex shrink-0 gap-1 opacity-70 transition-opacity group-hover:opacity-100">
            <Button
              variant="table-primary"
              iconOnly
              className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
              onClick={onEdit}
              aria-label={t.common.edit}
            >
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table-danger"
              iconOnly
              className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
              onClick={onDelete}
              aria-label={t.common.delete}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

export function RelationTypesSection({ isAdmin, onNewType, onEditType, onDeleteType }: Props) {
  const { t } = useI18n()
  const { data: types, isLoading } = useRelationTypes()

  const builtin = (types ?? []).filter(isRelationTypeProtected)
  const custom = (types ?? []).filter((row) => !isRelationTypeProtected(row))

  return (
    <div className="mt-10 border-t border-[var(--border-subtle)] pt-8">
      <SectionHead
        icon={GitBranch}
        title={t.settings.relationTypes}
        tone="brand"
        action={isAdmin && (
          <Button variant="primary" onClick={onNewType}>
            <Plus className="h-4 w-4" /> {t.settings.newRelationType}
          </Button>
        )}
      />

      {isLoading ? (
        <CardGridSkeleton count={4} className="h-28" />
      ) : (
      <div className="space-y-6">
        <div>
          <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">{t.settings.relationTypesBuiltin}</h3>
          {builtin.length === 0 ? (
            <EmptyState title={t.settings.noRelationTypes} />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {builtin.map((relationType) => (
                <RelationTypeCard
                  key={relationType.name}
                  relationType={relationType}
                  isAdmin={isAdmin}
                  onEdit={() => onEditType(relationType)}
                  onDelete={() => onDeleteType(relationType.id)}
                />
              ))}
            </div>
          )}
        </div>

        {custom.length > 0 && (
          <div>
            <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">{t.settings.relationTypesCustom}</h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {custom.map((relationType) => (
                <RelationTypeCard
                  key={relationType.id}
                  relationType={relationType}
                  isAdmin={isAdmin}
                  onEdit={() => onEditType(relationType)}
                  onDelete={() => onDeleteType(relationType.id)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  )
}
