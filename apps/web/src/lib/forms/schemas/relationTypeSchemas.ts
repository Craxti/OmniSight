import { z } from 'zod'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'
import { RELATION_TYPES } from '@/shared/constants'

type Messages = (typeof messages)[Locale]

const RELATION_TYPE_NAME_RE = /^[a-z][a-z0-9_]*$/

export function createRelationTypeFormSchema(t: Messages) {
  return z.object({
    id: z.number().optional(),
    name: z
      .string()
      .trim()
      .min(1, t.settings.relationTypeKey)
      .refine((value) => RELATION_TYPE_NAME_RE.test(value), {
        message: t.settings.relationTypeKeyHint,
      })
      .refine((value) => !(RELATION_TYPES as readonly string[]).includes(value), {
        message: t.settings.relationTypeReserved,
      }),
    description: z.string(),
    isOfficial: z.boolean().optional(),
  })
}

export type RelationTypeFormValues = z.infer<ReturnType<typeof createRelationTypeFormSchema>>
