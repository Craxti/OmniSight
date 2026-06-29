import { z } from 'zod'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'
import { isValidIpAddress } from '@/lib/ciFormValidation'

type Messages = (typeof messages)[Locale]

export function createUserCreateSchema(_t: Messages) {
  return z.object({
    email: z.string().trim().min(1).email(),
    role: z.enum(['viewer', 'editor', 'admin']),
    password: z.string().min(1),
  })
}

export function createPasswordResetSchema(_t: Messages) {
  return z.object({
    password: z.string().min(6),
  })
}

export function createCiTypeFormSchema(t: Messages) {
  return z.object({
    id: z.number().optional(),
    name: z.string().trim().min(1, t.settings.typeName),
    description: z.string(),
    schemaJson: z.string().refine(
      (value) => {
        if (!value.trim()) return true
        try {
          JSON.parse(value)
          return true
        } catch {
          return false
        }
      },
      { message: t.settings.errInvalidSchema },
    ),
  })
}

export function createRelationEditSchema(_t: Messages) {
  return z.object({
    id: z.number(),
    relation_type: z.string().min(1),
    status: z.string().min(1),
    data_source: z.string().min(1),
  })
}

export function createConnectorFormSchema(t: Messages) {
  return z
    .object({
      id: z.number().optional(),
      name: z.string(),
      connector_type: z.enum(['host', 'api', 'file', 'db', 'stream']),
      server_ci_mode: z.enum(['existing', 'new']),
      server_ci_id: z.string(),
      new_server_name: z.string(),
      new_server_hostname: z.string(),
      new_server_ip: z.string(),
      enabled: z.boolean(),
      auto_sync: z.boolean(),
      path: z.string(),
      ssh_host: z.string(),
      ssh_port: z.string(),
      ssh_user: z.string(),
      ssh_auth: z.enum(['password', 'key', 'agent']),
      ssh_password: z.string(),
      ssh_key_path: z.string(),
      url: z.string(),
      query: z.string(),
      database_url_env: z.string(),
      auth_type: z.enum(['none', 'basic', 'bearer', 'api_key']),
      token_env: z.string(),
      username_env: z.string(),
      password_env: z.string(),
    })
    .superRefine((data, ctx) => {
      if (!data.name.trim()) {
        ctx.addIssue({ code: 'custom', message: t.settings.connectors.needName, path: ['name'] })
      }
      if (data.connector_type === 'host' && data.server_ci_mode === 'existing' && !data.server_ci_id) {
        ctx.addIssue({ code: 'custom', message: t.settings.connectors.needServerCi, path: ['server_ci_id'] })
      }
      if (data.connector_type === 'host' && data.server_ci_mode === 'new') {
        if (!data.new_server_name.trim()) {
          ctx.addIssue({ code: 'custom', message: t.settings.connectors.needNewServerName, path: ['new_server_name'] })
        }
        if (!data.new_server_hostname.trim() && !data.new_server_ip.trim()) {
          ctx.addIssue({
            code: 'custom',
            message: t.settings.connectors.needNewServerHostOrIp,
            path: ['new_server_hostname'],
          })
        }
        const ip = data.new_server_ip.trim()
        if (ip && !isValidIpAddress(ip)) {
          ctx.addIssue({ code: 'custom', message: t.inventory.errInvalidIp, path: ['new_server_ip'] })
        }
      }
    })
}

export type ConnectorFormValues = z.infer<ReturnType<typeof createConnectorFormSchema>>

export const autodiscoverScanSchema = z.object({
  profileId: z.union([z.number(), z.literal('')]),
  selectedServers: z.array(z.number()).min(1),
  scopeMode: z.enum(['graph', 'all', 'filters']),
  scopeDepth: z.number().min(0).max(5),
  discoverRelations: z.boolean(),
  createMissingCi: z.boolean(),
  manualReview: z.boolean(),
})

export type AutodiscoverScanValues = z.infer<typeof autodiscoverScanSchema>

export type UserCreateValues = z.infer<ReturnType<typeof createUserCreateSchema>>
export type CiTypeFormValues = z.infer<ReturnType<typeof createCiTypeFormSchema>>
