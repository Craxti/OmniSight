/** Demo correlation alert rows for the Correlation UI (not synced from API). */

import { EXTERNAL_ID_FIELDS, type ExternalIdField } from '@/shared/domainConstants.generated'

export type AlertRow = Partial<Record<ExternalIdField, string>>

export const EXTERNAL_ID_FIELDS_SET = new Set<string>(EXTERNAL_ID_FIELDS)

export const DEMO_CORRELATION_ALERTS: AlertRow[] = [
  { hostname: 'app-01' },
  { ip: '10.0.0.5' },
  { externalId: 'ext-db-1' },
  { serviceCode: 'PAY', applicationCode: 'PAY-APP' },
]
