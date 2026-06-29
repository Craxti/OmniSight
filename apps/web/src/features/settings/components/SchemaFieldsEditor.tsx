import { GripVertical, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { fmt } from '@/i18n/messages'
import { externalIdFieldLabel } from '@/lib/domainLabels'
import {
  emptySchemaField,
  SCHEMA_FIELD_TYPES,
  type SchemaFieldDef,
  type SchemaFieldType,
} from '@/lib/ciTypeSchema'
import { EXTERNAL_ID_FIELDS_SET } from '@/shared/constants/demoAlerts'
import { cn } from '@/lib/utils'

const TYPE_BADGE: Record<SchemaFieldType, string> = {
  string: 'badge-indigo',
  integer: 'badge-amber',
  number: 'badge-green',
  boolean: 'badge-gray',
}

type Props = {
  fields: SchemaFieldDef[]
  onChange: (fields: SchemaFieldDef[]) => void
  duplicateError?: string
}

export function SchemaFieldsEditor({ fields, onChange, duplicateError }: Props) {
  const { t } = useI18n()

  const updateField = (index: number, patch: Partial<SchemaFieldDef>) => {
    onChange(fields.map((field, i) => (i === index ? { ...field, ...patch } : field)))
  }

  const removeField = (index: number) => {
    onChange(fields.filter((_, i) => i !== index))
  }

  const addField = () => {
    onChange([...fields, emptySchemaField()])
  }

  const externalKeys = fields
    .map((f) => f.key.trim())
    .filter((key) => key && EXTERNAL_ID_FIELDS_SET.has(key))

  const fieldTypeLabel = (type: SchemaFieldType) => t.settings.schemaFieldTypes[type]

  return (
    <div className="space-y-3">
      <p className="text-xs text-[var(--text-muted)]">{t.settings.typeSchemaHint}</p>

      {fields.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-hover)] px-4 py-8 text-center">
          <p className="text-sm text-[var(--text-muted)]">{t.settings.schemaNoFields}</p>
          <Button type="button" variant="secondary" className="mt-4" onClick={addField}>
            <Plus className="h-4 w-4" />
            {t.settings.schemaAddField}
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          {fields.map((field, index) => {
            const trimmedKey = field.key.trim()
            const isExternalId = trimmedKey && EXTERNAL_ID_FIELDS_SET.has(trimmedKey)
            return (
              <div
                key={index}
                className="group rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-hover)] p-3 transition-colors hover:border-[var(--rsm-color-brand)]/30"
              >
                <div className="flex items-start gap-2">
                  <GripVertical
                    className="mt-2.5 h-4 w-4 shrink-0 text-[var(--text-muted)] opacity-40"
                    aria-hidden
                  />
                  <div className="grid min-w-0 flex-1 gap-2 sm:grid-cols-12">
                    <div className="sm:col-span-4">
                      <label className="label text-[10px] uppercase tracking-wide">{t.settings.schemaFieldKey}</label>
                      <input
                        className="input font-mono text-sm"
                        value={field.key}
                        onChange={(e) => updateField(index, { key: e.target.value })}
                        placeholder="port"
                        list="ci-schema-known-keys"
                      />
                    </div>
                    <div className="sm:col-span-3">
                      <label className="label text-[10px] uppercase tracking-wide">{t.settings.schemaFieldType}</label>
                      <select
                        className="input"
                        value={field.type}
                        onChange={(e) => updateField(index, { type: e.target.value as SchemaFieldType })}
                      >
                        {SCHEMA_FIELD_TYPES.map((type) => (
                          <option key={type} value={type}>
                            {fieldTypeLabel(type)}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="sm:col-span-5">
                      <label className="label text-[10px] uppercase tracking-wide">{t.settings.schemaFieldDescription}</label>
                      <input
                        className="input"
                        value={field.description}
                        onChange={(e) => updateField(index, { description: e.target.value })}
                        placeholder={t.settings.schemaFieldDescriptionPlaceholder}
                      />
                    </div>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1.5 pt-5">
                    <span className={cn('badge text-[10px]', TYPE_BADGE[field.type])}>{field.type}</span>
                    <Button
                      type="button"
                      variant="table-danger"
                      iconOnly
                      className="min-h-9 min-w-9 opacity-60 group-hover:opacity-100"
                      onClick={() => removeField(index)}
                      aria-label={t.common.delete}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
                {isExternalId && (
                  <p className="mt-2 pl-6 text-xs text-[var(--text-info)]">
                    {fmt(t.settings.schemaExternalIdField, { field: externalIdFieldLabel(t, trimmedKey) })}
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}

      {fields.length > 0 && (
        <Button type="button" variant="secondary" className="w-full sm:w-auto" onClick={addField}>
          <Plus className="h-4 w-4" />
          {t.settings.schemaAddField}
        </Button>
      )}

      {duplicateError && (
        <p className="alert alert-warning text-xs" role="alert">
          {duplicateError}
        </p>
      )}

      {externalKeys.length > 1 && (
        <p className="hint text-xs" role="note">
          {fmt(t.settings.schemaExternalIdHint, {
            fields: externalKeys.map((k) => externalIdFieldLabel(t, k)).join(', '),
          })}
        </p>
      )}

      <datalist id="ci-schema-known-keys">
        {['hostname', 'ip', 'port', 'os', 'engine', 'serviceCode', 'applicationCode', 'health_url', 'sla_tier'].map((k) => (
          <option key={k} value={k} />
        ))}
      </datalist>
    </div>
  )
}
