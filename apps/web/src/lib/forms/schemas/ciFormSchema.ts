import { z } from 'zod'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'
import { isValidIpAddress } from '@/lib/ciFormValidation'
import {
  DEFAULT_CI_STATUS,
  DEFAULT_CRITICALITY,
  DEFAULT_ENVIRONMENT,
  SERVER_TYPE_NAME,
} from '@/shared/constants'

type Messages = (typeof messages)[Locale]

export function createCiFormSchema(t: Messages) {
  return z
    .object({
      name: z.string().trim().min(1, t.inventory.errName),
      type_name: z.string().min(1),
      status: z.string(),
      criticality: z.string().min(1, t.inventory.errCriticality),
      environment: z.string().trim().min(1, t.inventory.errEnvironment),
      owner: z.string().trim().min(1, t.inventory.errOwner),
      team: z.string(),
      description: z.string(),
      attributes: z.record(z.string(), z.string()),
    })
    .superRefine((data, ctx) => {
      const ip = data.attributes.ip?.trim()
      if (ip && !isValidIpAddress(ip)) {
        ctx.addIssue({ code: 'custom', message: t.inventory.errInvalidIp, path: ['attributes', 'ip'] })
      }
    })
}

export const ciFormSchemaDefaults = {
  name: '',
  type_name: SERVER_TYPE_NAME,
  status: DEFAULT_CI_STATUS,
  criticality: DEFAULT_CRITICALITY,
  environment: DEFAULT_ENVIRONMENT,
  owner: '',
  team: '',
  description: '',
  attributes: {} as Record<string, string>,
}

export type CiFormValues = z.infer<ReturnType<typeof createCiFormSchema>>
