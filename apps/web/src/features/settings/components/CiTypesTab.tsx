import { Boxes, Pencil, Plus, Trash2 } from 'lucide-react'
import { Button, EmptyState, CardGridSkeleton } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { fmt } from '@/i18n/messages'
import { countSchemaFields, listSchemaFieldKeys } from '@/lib/ciTypeSchema'
import type { CiType } from '@/shared/api/v1Inventory'
import { useCiTypes } from '@/shared/hooks/useCiTypes'
import { SectionHead } from '@/features/settings/components/SettingsUi'

type Props = {
  isAdmin: boolean
  onNewType: () => void
  onEditType: (ciType: CiType) => void
  onDeleteType: (id: number) => void
}

function typeDisplayName(t: ReturnType<typeof useI18n>['t'], name: string): string {
  const map = t.common.ciType as Record<string, string>
  return map[name] ?? name
}

function CiTypeCard({
  ciType,
  isAdmin,
  onEdit,
  onDelete,
}: {
  ciType: CiType
  isAdmin: boolean
  onEdit: () => void
  onDelete: () => void
}) {
  const { t } = useI18n()
  const fieldKeys = listSchemaFieldKeys(ciType.attribute_schema)
  const fieldCount = countSchemaFields(ciType.attribute_schema)
  const title = typeDisplayName(t, ciType.name)

  return (
    <div className="group card-hover-brand rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-hover)] p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="font-medium text-[var(--text-primary)]">{title}</div>
          {title !== ciType.name && (
            <div className="mt-0.5 font-mono text-xs text-[var(--text-muted)]">{ciType.name}</div>
          )}
          <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-xs text-[var(--text-muted)]">
            <span>ID {ciType.id}</span>
            {fieldCount > 0 && (
              <span className="badge badge-gray">{fmt(t.settings.schemaFieldsCount, { n: fieldCount })}</span>
            )}
            {ciType.is_official && <span className="badge badge-indigo">{t.settings.official}</span>}
            {ciType.is_import_draft && <span className="badge badge-amber">{t.settings.importDraft}</span>}
          </div>
          {ciType.description && (
            <p className="mt-2 line-clamp-2 text-xs text-[var(--text-muted)]">{ciType.description}</p>
          )}
          {fieldKeys.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {fieldKeys.slice(0, 6).map((key) => (
                <span key={key} className="rounded-md border border-[var(--border-subtle)] bg-[var(--bg-input)] px-1.5 py-0.5 font-mono text-[10px] text-[var(--text-secondary)]">
                  {key}
                </span>
              ))}
              {fieldKeys.length > 6 && (
                <span className="px-1 text-[10px] text-[var(--text-muted)]">+{fieldKeys.length - 6}</span>
              )}
            </div>
          )}
        </div>
        {isAdmin && (
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
            {!ciType.is_official && (
              <Button
                variant="table-danger"
                iconOnly
                className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
                onClick={onDelete}
                aria-label={t.common.delete}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export function CiTypesTab({ isAdmin, onNewType, onEditType, onDeleteType }: Props) {
  const { t } = useI18n()
  const { data: types, isLoading } = useCiTypes()

  const official = (types ?? []).filter((row) => row.is_official)
  const custom = (types ?? []).filter((row) => !row.is_official)

  const renderGrid = (items: CiType[]) => (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((ciType) => (
        <CiTypeCard
          key={ciType.id}
          ciType={ciType}
          isAdmin={isAdmin}
          onEdit={() => onEditType(ciType)}
          onDelete={() => onDeleteType(ciType.id)}
        />
      ))}
    </div>
  )

  return (
    <>
      <SectionHead
        icon={Boxes}
        title={t.settings.ciTypes}
        tone="brand"
        action={isAdmin && (
          <Button variant="primary" onClick={onNewType}>
            <Plus className="h-4 w-4" /> {t.settings.newType}
          </Button>
        )}
      />

      {isLoading ? (
        <CardGridSkeleton count={6} className="h-32" />
      ) : (types || []).length === 0 ? (
        <EmptyState title={t.settings.noTypes} />
      ) : (
        <div className="space-y-6">
          {official.length > 0 && (
            <div>
              <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">{t.settings.ciTypesBuiltin}</h3>
              {renderGrid(official)}
            </div>
          )}
          {custom.length > 0 && (
            <div>
              <h3 className="mb-3 text-sm font-medium text-[var(--text-secondary)]">{t.settings.ciTypesCustom}</h3>
              {renderGrid(custom)}
            </div>
          )}
        </div>
      )}
    </>
  )
}
