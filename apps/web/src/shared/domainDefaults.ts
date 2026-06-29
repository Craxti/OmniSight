/** Named defaults derived from generated domain constants — use instead of magic strings. */

import {
  CI_STATUSES,
  CRITICALITY_LEVELS,
  ENVIRONMENTS,
  RELATION_STATUSES,
  RELATION_TYPES,
  RSM_OFFICIAL_TYPE_NAMES,
} from '@/shared/domainConstants.generated'

export const DEFAULT_RELATION_TYPE = RELATION_TYPES[0]
export const DEFAULT_RELATION_STATUS = RELATION_STATUSES[0]
export const DEFAULT_CI_STATUS = CI_STATUSES[0]
export const DEFAULT_CRITICALITY = CRITICALITY_LEVELS[2]
export const DEFAULT_ENVIRONMENT = ENVIRONMENTS[3]
export const DEFAULT_DATA_SOURCE = 'manual' as const
export const BUSINESS_SERVICE_TYPE_NAME = RSM_OFFICIAL_TYPE_NAMES[0]
export const SERVER_TYPE_NAME = RSM_OFFICIAL_TYPE_NAMES[4]
