import { useI18n } from '@/context/useI18n'
import { EXTERNAL_ID_FIELDS_SET } from '@/shared/constants'
import { FormField } from '@/shared/components/FormField'
import type { AttributeSchema } from '@/shared/inventory/ciAttributes'

export type { AttributeSchema } from '@/shared/inventory/ciAttributes'
export { mergeAttributesToExternal, schemaForType } from '@/shared/inventory/ciAttributes'

export function AttributeFields({
  schema,
  values,
  onChange,
}: {
  schema: AttributeSchema | null | undefined
  values: Record<string, string>
  onChange: (next: Record<string, string>) => void
}) {
  const { t } = useI18n()
  const props = schema?.properties || {}
  const keys = Object.keys(props).filter((k) => !EXTERNAL_ID_FIELDS_SET.has(k))

  if (keys.length === 0) {
    return (
      <p className="text-xs text-[var(--text-muted)]">{t.inventory.noTypeAttrs}</p>
    )
  }

  return (
    <div className="grid gap-3 md:grid-cols-2">
      {keys.map((key) => (
        <FormField
          key={key}
          label={`${key}${props[key]?.type ? ` (${props[key].type})` : ''}`}
          htmlFor={`attr-${key}`}
        >
          <input
            id={`attr-${key}`}
            className="input"
            value={values[key] || ''}
            onChange={(e) => onChange({ ...values, [key]: e.target.value })}
            placeholder={props[key]?.description}
          />
        </FormField>
      ))}
    </div>
  )
}
