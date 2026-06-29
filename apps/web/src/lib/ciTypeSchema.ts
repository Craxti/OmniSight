export type SchemaFieldType = 'string' | 'integer' | 'number' | 'boolean'

export type SchemaFieldDef = {
  key: string
  type: SchemaFieldType
  description: string
}

export const SCHEMA_FIELD_TYPES: SchemaFieldType[] = ['string', 'integer', 'number', 'boolean']

export const DEFAULT_ATTRIBUTE_SCHEMA = { properties: {} } as const

type SchemaProperty = { type?: string; description?: string }

function normalizeFieldType(value?: string): SchemaFieldType {
  if (value === 'integer' || value === 'number' || value === 'boolean') return value
  return 'string'
}

export function parseSchemaFields(json: string): { fields: SchemaFieldDef[]; error?: 'invalid_json' } {
  if (!json.trim()) return { fields: [] }
  try {
    const parsed = JSON.parse(json) as { properties?: Record<string, SchemaProperty> }
    const properties = parsed?.properties ?? {}
    const fields = Object.entries(properties).map(([key, def]) => ({
      key,
      type: normalizeFieldType(def?.type),
      description: def?.description ?? '',
    }))
    return { fields }
  } catch {
    return { fields: [], error: 'invalid_json' }
  }
}

export function buildSchemaJson(fields: SchemaFieldDef[]): string {
  const properties: Record<string, SchemaProperty> = {}
  for (const field of fields) {
    const key = field.key.trim()
    if (!key) continue
    const prop: SchemaProperty = { type: field.type }
    const description = field.description.trim()
    if (description) prop.description = description
    properties[key] = prop
  }
  return JSON.stringify({ properties }, null, 2)
}

export function listSchemaFieldKeys(schema: unknown): string[] {
  if (!schema || typeof schema !== 'object') return []
  const properties = (schema as { properties?: Record<string, unknown> }).properties
  if (!properties || typeof properties !== 'object') return []
  return Object.keys(properties)
}

export function countSchemaFields(schema: unknown): number {
  return listSchemaFieldKeys(schema).length
}

export function hasDuplicateSchemaKeys(fields: SchemaFieldDef[]): boolean {
  const seen = new Set<string>()
  for (const field of fields) {
    const key = field.key.trim()
    if (!key) continue
    if (seen.has(key)) return true
    seen.add(key)
  }
  return false
}

export function emptySchemaField(): SchemaFieldDef {
  return { key: '', type: 'string', description: '' }
}
