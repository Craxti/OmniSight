export type StoredPosition = { x: number; y: number }

/** Normalize relation filter for layout buckets (depth-independent). */
export function normalizeRelationFilter(relationFilter: string): string {
  return relationFilter || '*'
}
