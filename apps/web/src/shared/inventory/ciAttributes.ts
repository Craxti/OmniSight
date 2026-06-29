import { EXTERNAL_ID_FIELDS } from '@/shared/constants'

interface SchemaProperty {
  type?: string
  description?: string
}

export interface AttributeSchema {
  properties?: Record<string, SchemaProperty>
}

export function schemaForType(
  types: Array<{ name: string; attribute_schema?: unknown }> | undefined,
  typeName: string,
): AttributeSchema | null {
  const typeRow = types?.find((x) => x.name === typeName)
  if (!typeRow?.attribute_schema) return null
  return typeRow.attribute_schema as AttributeSchema
}

export function mergeAttributesToExternal(values: Record<string, string>) {
  const external: Record<string, string> = {}
  for (const k of EXTERNAL_ID_FIELDS) {
    if (values[k]) external[k] = values[k]
  }
  const attrs = { ...values }
  for (const k of EXTERNAL_ID_FIELDS) delete attrs[k]
  return { attributes: attrs, external_ids: external }
}
