import { RELATION_TYPE_ALIASES, RELATION_TYPES } from '@/shared/constants'

export class RelationTypeValidationError extends Error {
  constructor(value: string) {
    super(`Invalid relation type: ${value}`)
    this.name = 'RelationTypeValidationError'
  }
}

/** Normalize relation type labels to canonical backend values (throws on unknown). */
export function normalizeRelationType(
  value: string,
  allowed: readonly string[] = RELATION_TYPES,
): string {
  const trimmed = value.trim()
  if (!trimmed) return trimmed
  const alias = RELATION_TYPE_ALIASES[trimmed.toLowerCase() as keyof typeof RELATION_TYPE_ALIASES]
  const normalized = alias ?? trimmed
  if (!allowed.includes(normalized)) {
    throw new RelationTypeValidationError(value)
  }
  return normalized
}

/** Safe variant for optional UI fields — returns empty string instead of throwing. */
export function tryNormalizeRelationType(value: string, allowed?: readonly string[]): string {
  try {
    return normalizeRelationType(value, allowed)
  } catch {
    return value.trim()
  }
}
