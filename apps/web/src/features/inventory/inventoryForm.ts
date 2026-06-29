import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'
import { isValidIpAddress } from '@/lib/ciFormValidation'
import {
  BUSINESS_SERVICE_TYPE_NAME,
  DEFAULT_CI_STATUS,
  DEFAULT_CRITICALITY,
  DEFAULT_ENVIRONMENT,
  RSM_OFFICIAL_TYPE_NAMES,
  SERVER_TYPE_NAME,
  type CiStatus,
  type CriticalityLevel,
  type Environment,
} from '@/shared/constants'

export type { AttributeSchema } from '@/shared/inventory/ciAttributes'
export { mergeAttributesToExternal, schemaForType } from '@/shared/inventory/ciAttributes'

type Messages = (typeof messages)[Locale]

export const CI_TEMPLATES: Record<string, Partial<CiFormState>> = Object.fromEntries(
  RSM_OFFICIAL_TYPE_NAMES.slice(0, 5).map((name) => {
    const base: Partial<CiFormState> = { type_name: name, attributes: {} }
    if (name === SERVER_TYPE_NAME) return [name, { ...base, attributes: { hostname: '', ip: '', port: '22', os: 'Linux' } }]
    if (name === 'Database') return [name, { ...base, attributes: { hostname: '', ip: '', engine: 'PostgreSQL', port: '5432' } }]
    if (name === 'Application') return [name, { ...base, attributes: { hostname: '', serviceCode: '', applicationCode: '', health_url: '' } }]
    if (name === BUSINESS_SERVICE_TYPE_NAME) return [name, { ...base, attributes: { serviceCode: '', sla_tier: 'P1' } }]
    if (name === 'Technical Component') return [name, { ...base, attributes: { hostname: '', ip: '', port: '', engine: '', runtime_status: 'RUNNING' } }]
    return [name, base]
  }),
)

export type CiFormState = {
  name: string
  type_name: string
  status: CiStatus
  criticality: CriticalityLevel
  environment: Environment
  owner: string
  team: string
  description: string
  attributes: Record<string, string>
}

export const defaultCiForm: CiFormState = {
  name: '',
  type_name: SERVER_TYPE_NAME,
  status: DEFAULT_CI_STATUS,
  criticality: DEFAULT_CRITICALITY,
  environment: DEFAULT_ENVIRONMENT,
  owner: '',
  team: '',
  description: '',
  attributes: {},
}

export function validateCiForm(form: CiFormState, t: Messages): string | null {
  if (!form.name.trim()) return t.inventory.errName
  if (!form.owner.trim()) return t.inventory.errOwner
  if (!form.environment.trim()) return t.inventory.errEnvironment
  if (!form.criticality) return t.inventory.errCriticality
  const ip = form.attributes.ip?.trim()
  if (ip && !isValidIpAddress(ip)) return t.inventory.errInvalidIp
  return null
}
