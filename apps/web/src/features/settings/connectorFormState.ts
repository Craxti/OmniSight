import type { SyncConnectorInput } from '@/shared/api/autodiscover'
import { isValidIpAddress } from '@/lib/ciFormValidation'

export type HostSshAuth = 'password' | 'key' | 'agent'
export type ServerCiMode = 'existing' | 'new'

export type ConnectorFormState = {
  id?: number
  name: string
  connector_type: 'host' | 'api' | 'file' | 'db' | 'stream'
  server_ci_mode: ServerCiMode
  server_ci_id: string
  new_server_name: string
  new_server_hostname: string
  new_server_ip: string
  enabled: boolean
  auto_sync: boolean
  path: string
  ssh_host: string
  ssh_port: string
  ssh_user: string
  ssh_auth: HostSshAuth
  ssh_password: string
  ssh_key_path: string
  url: string
  query: string
  database_url_env: string
  auth_type: 'none' | 'basic' | 'bearer' | 'api_key'
  token_env: string
  username_env: string
  password_env: string
}

export function parseSshHostTarget(host: string): { hostname: string; ip: string } {
  const v = host.trim()
  if (!v) return { hostname: '', ip: '' }
  const looksLikeIp = /^[\d.]+$/.test(v) || (v.includes(':') && !/\s/.test(v))
  if (looksLikeIp && isValidIpAddress(v)) return { hostname: '', ip: v }
  return { hostname: v, ip: '' }
}

export const EMPTY_CONNECTOR_FORM: ConnectorFormState = {
  name: '',
  connector_type: 'host',
  server_ci_mode: 'existing',
  server_ci_id: '',
  new_server_name: '',
  new_server_hostname: '',
  new_server_ip: '',
  enabled: true,
  auto_sync: false,
  path: '',
  ssh_host: '',
  ssh_port: '22',
  ssh_user: 'root',
  ssh_auth: 'password',
  ssh_password: '',
  ssh_key_path: '',
  url: '',
  query: '',
  database_url_env: 'OMNISIGHT_DATABASE_URL',
  auth_type: 'none',
  token_env: '',
  username_env: '',
  password_env: '',
}

export function connectorFormFromInitial(initial: {
  id: number
  name: string
  connector_type: string
  server_ci_id?: number | null
  enabled: boolean
  auto_sync?: boolean
  config?: Record<string, unknown>
}): ConnectorFormState {
  const cfg = initial.config ?? {}
  const snapshot = String(cfg.snapshot_path ?? cfg.path ?? '')
  return {
    id: initial.id,
    name: initial.name,
    connector_type: initial.connector_type as ConnectorFormState['connector_type'],
    server_ci_mode: 'existing',
    server_ci_id: initial.server_ci_id ? String(initial.server_ci_id) : '',
    new_server_name: '',
    new_server_hostname: '',
    new_server_ip: '',
    enabled: initial.enabled,
    auto_sync: initial.auto_sync ?? false,
    path: snapshot,
    ssh_host: String(cfg.ssh_host ?? ''),
    ssh_port: String(cfg.ssh_port ?? '22'),
    ssh_user: String(cfg.ssh_user ?? 'root'),
    ssh_auth: snapshot ? 'agent' : (cfg.ssh_key_path ? 'key' : 'password'),
    ssh_password: '',
    ssh_key_path: String(cfg.ssh_key_path ?? ''),
    url: String(cfg.url ?? ''),
    query: String(cfg.query ?? ''),
    database_url_env: 'OMNISIGHT_DATABASE_URL',
    auth_type: 'none',
    token_env: '',
    username_env: '',
    password_env: '',
  }
}

export function buildConnectorSubmitPayload(form: ConnectorFormState): SyncConnectorInput {
  const config: Record<string, unknown> = {}
  let credentials: SyncConnectorInput['credentials'] | null = null

  if (form.connector_type === 'host') {
    const snapshot = form.path.trim()
    if (form.ssh_host.trim()) config.ssh_host = form.ssh_host.trim()
    if (form.ssh_port.trim()) config.ssh_port = Number(form.ssh_port.trim()) || 22
    if (form.ssh_user.trim()) config.ssh_user = form.ssh_user.trim()
    if (snapshot) {
      config.snapshot_path = snapshot
      config.mode = 'snapshot'
    } else {
      config.mode = 'ssh'
      if (form.ssh_auth === 'key' && form.ssh_key_path.trim()) {
        config.ssh_key_path = form.ssh_key_path.trim()
      }
      credentials = {
        auth_type: form.ssh_auth === 'key' ? 'ssh_key' : 'basic',
        username: form.ssh_user.trim() || 'root',
      }
      if (form.ssh_auth === 'password' && form.ssh_password.trim()) {
        credentials.password = form.ssh_password.trim()
      }
      if (form.ssh_auth === 'key' && form.ssh_key_path.trim()) {
        credentials.private_key_path = form.ssh_key_path.trim()
      }
      if (form.ssh_auth === 'agent') {
        credentials = { auth_type: 'none', username: form.ssh_user.trim() || 'root' }
      }
    }
  } else if (form.connector_type === 'file') {
    config.path = form.path.trim()
  } else if (form.connector_type === 'api') {
    config.url = form.url.trim()
    credentials = { auth_type: form.auth_type }
    if (form.auth_type === 'bearer' && form.token_env.trim()) credentials.token_env = form.token_env.trim()
    if (form.auth_type === 'basic') {
      if (form.username_env.trim()) credentials.username_env = form.username_env.trim()
      if (form.password_env.trim()) credentials.password_env = form.password_env.trim()
    }
  } else if (form.connector_type === 'db') {
    config.query = form.query.trim()
    credentials = { auth_type: 'none' }
    if (form.database_url_env.trim()) credentials.database_url_env = form.database_url_env.trim()
  }

  return {
    name: form.name.trim(),
    connector_type: form.connector_type,
    server_ci_id: form.server_ci_id ? Number(form.server_ci_id) : null,
    config,
    credentials,
    enabled: form.enabled,
    auto_sync: form.auto_sync,
  }
}
