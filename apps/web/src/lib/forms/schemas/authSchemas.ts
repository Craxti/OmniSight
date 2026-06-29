import { z } from 'zod'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'

type Messages = (typeof messages)[Locale]

export function createLoginSchema(_t: Messages) {
  return z.object({
    email: z.string().trim().min(1).email(),
    password: z.string().min(1),
  })
}

export function createChangePasswordSchema(t: Messages) {
  return z
    .object({
      currentPassword: z.string().min(1),
      newPassword: z.string().min(6, t.changePassword.tooShort),
      confirmPassword: z.string().min(1),
    })
    .refine((data) => data.newPassword === data.confirmPassword, {
      message: t.changePassword.mismatch,
      path: ['confirmPassword'],
    })
}

export function createRelationFormSchema(t: Messages) {
  return z.object({
    source_ci_id: z.string().min(1, t.relations.errSource),
    target_ci_id: z.string().min(1, t.relations.errTarget),
    relation_type: z.string().min(1),
    data_source: z.string().min(1),
  })
}
