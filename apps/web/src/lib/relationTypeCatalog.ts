import { RELATION_TYPES } from '@/shared/constants'
import type { RelationType } from '@/shared/api/v1Inventory'

export function isBuiltinRelationType(name: string): boolean {
  return (RELATION_TYPES as readonly string[]).includes(name)
}

/** Merge API catalog with built-in relation types (always show defaults first). */
export function mergeRelationTypes(apiTypes: RelationType[] | undefined): RelationType[] {
  const byName = new Map((apiTypes ?? []).map((row) => [row.name, row]))
  const merged: RelationType[] = []
  let syntheticId = -1

  for (const name of RELATION_TYPES) {
    const existing = byName.get(name)
    merged.push(
      existing
        ? { ...existing, is_official: true }
        : { id: syntheticId--, name, is_official: true },
    )
    byName.delete(name)
  }

  for (const custom of [...byName.values()].sort((a, b) => a.name.localeCompare(b.name))) {
    merged.push({ ...custom, is_official: custom.is_official ?? false })
  }

  return merged
}

export function isRelationTypeProtected(row: RelationType): boolean {
  return row.is_official === true || isBuiltinRelationType(row.name)
}
