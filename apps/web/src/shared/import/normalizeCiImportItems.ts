import { EXTERNAL_ID_FIELDS } from '@/shared/constants'
import { normalizeFieldKey } from '@/shared/import/normalizeFieldKey'

export function normalizeCiImportItems(items: unknown[]): unknown[] {
  return items.map((item) => {
    if (!item || typeof item !== 'object') return item
    const row = item as Record<string, unknown>
    const external_ids = (row.external_ids ?? {}) as Record<string, unknown>
    const normalizedRow: Record<string, unknown> = { ...row }

    for (const [key, val] of Object.entries(row)) {
      if (key === 'external_ids') continue
      const canonical = normalizeFieldKey(key)
      if (canonical !== key) {
        if (val !== undefined && val !== null && String(val).trim() !== '') {
          external_ids[canonical] = val
        }
        delete normalizedRow[key]
      }
    }

    for (const key of EXTERNAL_ID_FIELDS) {
      const val = normalizedRow[key]
      if (val !== undefined && val !== null && String(val).trim() !== '') {
        external_ids[key] = val
      }
    }

    return { ...normalizedRow, external_ids }
  })
}
