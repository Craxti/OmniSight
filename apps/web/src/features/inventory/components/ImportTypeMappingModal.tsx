import { Fragment, useEffect, useMemo, useState } from 'react'
import { Modal, Button } from '@/components/ui'
import { cn } from '@/lib/utils'
import { FormField } from '@/shared/components/FormField'
import { useI18n } from '@/context/useI18n'
import { fmt } from '@/i18n/messages'
import type { ImportTypeMappingEntry, ImportTypePreview } from '@/shared/api/ci'
import { buildMappingEntries, initialMappingRow, type MappingRowState } from '@/features/inventory/importTypeMapping'

type Props = {
  open: boolean
  preview: ImportTypePreview | null
  pending?: boolean
  onClose: () => void
  onConfirm: (mappings: ImportTypeMappingEntry[]) => void
}

export function ImportTypeMappingModal({ open, preview, pending, onClose, onConfirm }: Props) {
  const { t } = useI18n()
  const [rows, setRows] = useState<MappingRowState[]>([])

  useEffect(() => {
    if (!preview) {
      setRows([])
      return
    }
    setRows(preview.proposals.map(initialMappingRow))
  }, [preview])

  const existingTypes = preview?.existing_types ?? []

  const invalidRows = useMemo(
    () =>
      rows.filter((row) => {
        if (row.status === 'matched') return false
        if (row.createNew) return !row.draftName.trim()
        return !row.target_type_id
      }),
    [rows],
  )

  const updateRow = (sourceType: string, patch: Partial<MappingRowState>) => {
    setRows((prev) => prev.map((row) => (row.source_type === sourceType ? { ...row, ...patch } : row)))
  }

  const submit = () => {
    onConfirm(buildMappingEntries(rows))
  }

  if (!preview) return null

  return (
    <Modal open={open} onClose={onClose} title={t.inventory.importTypeMappingTitle} wide>
      <div className="space-y-4" data-testid="import-type-mapping-modal">
        <p className="text-sm text-[var(--text-muted)]">{t.inventory.importTypeMappingHint}</p>
        {preview.missing_type_items > 0 && (
          <p className="alert alert-warning">
            {fmt(t.inventory.importTypeMissing, { n: preview.missing_type_items })}
          </p>
        )}

        <div className="overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
          <table className="w-full min-w-[720px] text-sm">
            <thead className="bg-[var(--surface-muted)] text-left text-xs text-[var(--text-muted)]">
              <tr>
                <th className="px-3 py-2">{t.inventory.importTypeSource}</th>
                <th className="px-3 py-2">{t.inventory.importTypeCount}</th>
                <th className="px-3 py-2">{t.inventory.importTypeMapTo}</th>
                <th className="px-3 py-2">{t.inventory.importTypeCreateNew}</th>
                <th className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <Fragment key={row.source_type}>
                  <tr className="border-t border-[var(--border-subtle)]">
                    <td className="px-3 py-2 font-medium">{row.source_type}</td>
                    <td className="px-3 py-2 text-[var(--text-muted)]">{row.item_count}</td>
                    <td className="px-3 py-2">
                      {row.status === 'matched' ? (
                        <span className="badge badge-indigo">{row.target_type_id ? existingTypes.find((t) => t.id === row.target_type_id)?.name : '—'}</span>
                      ) : (
                        <select
                          className="input !py-1.5 text-xs"
                          disabled={row.createNew}
                          value={row.target_type_id ?? ''}
                          onChange={(e) =>
                            updateRow(row.source_type, {
                              target_type_id: e.target.value ? Number(e.target.value) : null,
                              action: 'use_existing',
                            })
                          }
                        >
                          <option value="">{t.inventory.importTypeSelectExisting}</option>
                          {existingTypes.map((typeOpt) => (
                            <option key={typeOpt.id} value={typeOpt.id}>
                              {typeOpt.name}
                            </option>
                          ))}
                        </select>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      {row.status === 'matched' ? (
                        <span className="text-xs text-[var(--text-muted)]">—</span>
                      ) : (
                        <div className="flex gap-2">
                          <Button
                            variant="secondary"
                            className={cn('!px-2 !py-1 text-xs', row.createNew && 'btn-toggle-active')}
                            onClick={() => updateRow(row.source_type, { createNew: true, action: 'create_new' })}
                          >
                            {t.common.yes}
                          </Button>
                          <Button
                            variant="secondary"
                            className={cn('!px-2 !py-1 text-xs', !row.createNew && 'btn-toggle-active')}
                            onClick={() => updateRow(row.source_type, { createNew: false, action: 'use_existing' })}
                          >
                            {t.common.no}
                          </Button>
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      {row.status !== 'matched' && row.createNew && (
                        <Button
                          variant="secondary"
                          className="!px-2 !py-1 text-xs"
                          onClick={() => updateRow(row.source_type, { expanded: !row.expanded })}
                        >
                          {row.expanded ? t.inventory.importTypeHideDraft : t.inventory.importTypeEditDraft}
                        </Button>
                      )}
                    </td>
                  </tr>
                  {row.expanded && row.createNew && row.status !== 'matched' && (
                    <tr className="border-t border-[var(--border-subtle)] bg-[var(--surface-muted)]/40">
                      <td colSpan={5} className="px-3 py-3">
                        <div className="grid gap-3 md:grid-cols-2">
                          <FormField label={t.settings.typeName}>
                            <input
                              className="input"
                              value={row.draftName}
                              onChange={(e) => updateRow(row.source_type, { draftName: e.target.value })}
                            />
                          </FormField>
                          <FormField label={t.settings.typeDescription}>
                            <input
                              className="input"
                              value={row.draftDescription}
                              onChange={(e) => updateRow(row.source_type, { draftDescription: e.target.value })}
                            />
                          </FormField>
                          <FormField label={t.settings.typeSchema} className="md:col-span-2">
                            <textarea
                              className="input min-h-[120px] font-mono text-xs"
                              value={row.draftSchemaJson}
                              onChange={(e) => updateRow(row.source_type, { draftSchemaJson: e.target.value })}
                            />
                          </FormField>
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose} disabled={pending}>
            {t.common.cancel}
          </Button>
          <Button
            variant="primary"
            data-testid="import-type-mapping-confirm"
            disabled={pending || invalidRows.length > 0}
            onClick={submit}
          >
            {t.inventory.importTypeConfirm}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
