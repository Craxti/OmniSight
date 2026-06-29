import { FIELD_ALIASES } from '@/shared/constants'

/** Map import/autodiscover field aliases to canonical external-id keys (mirrors API normalize_field_key). */
export function normalizeFieldKey(key: string): string {
  return FIELD_ALIASES[key as keyof typeof FIELD_ALIASES] ?? key
}
