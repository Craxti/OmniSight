const PRIORITY_KEYS = [
  'name',
  'type_name',
  'type',
  'status',
  'relation_type',
  'source_name',
  'target_name',
  'owner',
  'environment',
]

export const AUDIT_DIFF_INLINE_LIMIT = 2
export const AUDIT_DIFF_VALUE_MAX_LEN = 40

export function formatAuditValue(v: unknown): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

export function truncateAuditValue(value: string, maxLen = AUDIT_DIFF_VALUE_MAX_LEN): string {
  if (value.length <= maxLen) return value
  return `${value.slice(0, maxLen - 1)}…`
}

export function getChangedAuditKeys(
  oldValue: Record<string, unknown> | null,
  newValue: Record<string, unknown> | null,
): string[] {
  if (oldValue && !newValue) {
    return sortAuditKeys(
      PRIORITY_KEYS.filter((key) => oldValue[key] !== undefined && oldValue[key] !== null),
    )
  }
  if (!oldValue && newValue) {
    return sortAuditKeys(
      PRIORITY_KEYS.filter((key) => newValue[key] !== undefined && newValue[key] !== null),
    )
  }
  const keys = new Set([...Object.keys(oldValue || {}), ...Object.keys(newValue || {})])
  return sortAuditKeys(
    [...keys].filter((k) => JSON.stringify(oldValue?.[k]) !== JSON.stringify(newValue?.[k])),
  )
}

export function isAuditRemoval(
  oldValue: Record<string, unknown> | null,
  newValue: Record<string, unknown> | null,
): boolean {
  return Boolean(oldValue && !newValue)
}

export function isAuditCreation(
  oldValue: Record<string, unknown> | null,
  newValue: Record<string, unknown> | null,
): boolean {
  return Boolean(!oldValue && newValue)
}

export function sortAuditKeys(keys: string[]): string[] {
  return [...keys].sort((a, b) => {
    const ai = PRIORITY_KEYS.indexOf(a)
    const bi = PRIORITY_KEYS.indexOf(b)
    if (ai === -1 && bi === -1) return a.localeCompare(b)
    if (ai === -1) return 1
    if (bi === -1) return -1
    return ai - bi
  })
}
