/** Re-export shared contract constants for backward-compatible `@/shared` imports. */

export {
  RELATION_TYPES,
  RELATION_TYPE_ALIASES,
  RELATION_STATUSES,
  CI_STATUSES,
  BULK_CI_STATUSES,
  CRITICALITY_LEVELS,
  ENVIRONMENTS,
  ROLES,
  RSM_OFFICIAL_TYPE_NAMES,
  EXTERNAL_ID_FIELDS,
  FIELD_ALIASES,
  type RelationType,
  type CiStatus,
  type CriticalityLevel,
  type Environment,
  type ExternalIdField,
  type Role,
} from '@omnisight/contract'
