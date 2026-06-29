import { normalizeRelationType, RelationTypeValidationError } from '@/lib/relationType'

export type NormalizedRelationImportItem = {
  source_ci_id?: number
  target_ci_id?: number
  source_name?: string
  target_name?: string
  relation_type: string
  status?: string
  data_source?: string
  _invalid_relation_type?: boolean
}

export function normalizeRelationImportItems(items: unknown[]): NormalizedRelationImportItem[] {
  return items.map((item) => {
    if (!item || typeof item !== 'object') {
      return { relation_type: '' }
    }
    const row = item as Record<string, unknown>
    const rawType = String(row.relation_type ?? row.type ?? row.relation ?? '')
    let relation_type: string
    let _invalid_relation_type = false
    try {
      relation_type = normalizeRelationType(rawType)
    } catch (err) {
      if (err instanceof RelationTypeValidationError) {
        relation_type = rawType.trim()
        _invalid_relation_type = Boolean(relation_type)
      } else {
        throw err
      }
    }
    return {
      source_ci_id: row.source_ci_id != null ? Number(row.source_ci_id) : undefined,
      target_ci_id: row.target_ci_id != null ? Number(row.target_ci_id) : undefined,
      source_name: row.source_name != null ? String(row.source_name) : undefined,
      target_name: row.target_name != null ? String(row.target_name) : undefined,
      relation_type,
      status: row.status != null ? String(row.status) : undefined,
      data_source:
        row.data_source != null ? String(row.data_source) : row.source != null ? String(row.source) : undefined,
      ...(_invalid_relation_type ? { _invalid_relation_type: true } : {}),
    }
  })
}
