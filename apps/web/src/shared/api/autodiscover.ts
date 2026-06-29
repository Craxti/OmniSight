import { api, buildQuery } from '@/shared/api/client'
import { paths } from '@/shared/api/paths'
import {
  type ApplyV1Response,
  type AutodiscoverItemsV1Response,
  type ConnectorSyncV1Response,
  type ConnectorTestV1Response,
  type ConnectorV1Response,
  type DeleteResultV1Response,
  type ScanV1Response,
  unwrapApply,
  unwrapAutodiscoverItems,
  unwrapConnector,
  unwrapConnectorSync,
  unwrapConnectorTest,
  unwrapDeleteResult,
  unwrapScan,
} from '@/shared/api/v1Autodiscover'

export type AutodiscoverMappingKind = 'field' | 'relation' | 'ci_create'

export type AutodiscoverFieldMapping = {
  mapping_id: string
  mapping_kind: AutodiscoverMappingKind
  ci_id: number | null
  ci_name: string
  target_ci_id?: number | null
  target_ci_name?: string | null
  relation_type?: string | null
  field: string
  current_value: string | null
  discovered_value: string
  source_server: string
  source_connector: string
  confidence: number
  status: 'auto' | 'needs_confirmation' | 'conflict' | 'unchanged' | 'applied'
  selected: boolean
}

export type AutodiscoverApplyResponse = {
  applied: number
  skipped: number
  errors: string[]
  updated_ci_ids: number[]
  created_cis: number
  applied_relations: number
}

export type AutodiscoverScanResponse = {
  run_id: number
  status: string
  sources_processed: number
  sources_ok: number
  fields_found: number
  auto_count: number
  needs_confirmation_count: number
  conflict_count: number
  relation_count: number
  ci_create_count: number
  sources: Array<{
    connector_id?: number | null
    connector_name?: string | null
    connector_type?: string | null
    server_ci_id?: number | null
    server_name?: string | null
    hostname?: string | null
    ok: boolean
    records_found: number
    error: string | null
    duration_ms?: number
    attempts?: number
  }>
  mappings: AutodiscoverFieldMapping[]
  discovered_schema: Record<string, unknown>
  schema_diff?: Record<string, unknown> | null
  apply_result?: AutodiscoverApplyResponse | null
}

export type SyncProfile = {
  id: number
  name: string
  description?: string | null
  connector_ids: number[]
  source_types: string[]
  scope_mode: string
  scope_config: Record<string, unknown>
  mapping_rules: Record<string, unknown>
  auto_apply_threshold: number
  schema_version: string
  last_run_id?: number | null
}

export type SyncConnectorCredentials = {
  auth_type?: 'none' | 'basic' | 'bearer' | 'api_key' | 'ssh_key'
  username?: string
  password?: string
  username_env?: string
  password_env?: string
  private_key?: string
  private_key_path?: string
  private_key_path_env?: string
  token?: string
  token_env?: string
  api_key?: string
  api_key_env?: string
  api_key_header?: string
  database_url?: string
  database_url_env?: string
}

export type SyncConnector = {
  id: number
  name: string
  connector_type: string
  server_ci_id?: number | null
  config: Record<string, unknown>
  has_credentials: boolean
  timeout_seconds: number
  max_retries: number
  read_only: boolean
  enabled: boolean
  auto_sync: boolean
  schema_version: string
}

export type SyncConnectorInput = {
  name: string
  connector_type: 'host' | 'api' | 'file' | 'db' | 'stream'
  server_ci_id?: number | null
  config: Record<string, unknown>
  credentials?: SyncConnectorCredentials | null
  timeout_seconds?: number
  max_retries?: number
  enabled?: boolean
  auto_sync?: boolean
}

export type ConnectorSyncResult = {
  run_id: number
  status: string
  sources_ok: number
  fields_found: number
  apply_result?: AutodiscoverApplyResponse | null
  error?: string | null
}

export type AutodiscoverScanRequest = {
  profile_id?: number
  connector_ids?: number[]
  server_ci_ids?: number[]
  source_types?: string[]
  scope_mode?: 'graph' | 'filters' | 'all'
  scope_config?: Record<string, unknown>
  scope_depth?: number
  root_ci_id?: number
  discover_relations?: boolean
  create_missing_ci?: boolean
  auto_apply?: boolean
}

export type ConnectorTestResult = {
  ok: boolean
  records_found: number
  error: string | null
  duration_ms: number
}

export const autodiscoverApi = {
  profiles: async () => {
    const body = await api<AutodiscoverItemsV1Response<SyncProfile>>(paths.autodiscover.profiles)
    return unwrapAutodiscoverItems(body)
  },
  connectors: async (enabledOnly = false) => {
    const body = await api<AutodiscoverItemsV1Response<SyncConnector>>(
      `${paths.autodiscover.connectors}${buildQuery({ enabled_only: String(enabledOnly) })}`,
    )
    return unwrapAutodiscoverItems(body)
  },
  createConnector: async (body: SyncConnectorInput) => {
    const response = await api<ConnectorV1Response>(paths.autodiscover.connectors, {
      method: 'POST',
      body: JSON.stringify(body),
    })
    return unwrapConnector(response)
  },
  updateConnector: async (id: number, body: Partial<SyncConnectorInput>) => {
    const response = await api<ConnectorV1Response>(paths.autodiscover.connector(id), {
      method: 'PATCH',
      body: JSON.stringify(body),
    })
    return unwrapConnector(response)
  },
  deleteConnector: async (id: number) => {
    const response = await api<DeleteResultV1Response>(paths.autodiscover.connector(id), { method: 'DELETE' })
    return unwrapDeleteResult(response)
  },
  testConnector: async (id: number) => {
    const response = await api<ConnectorTestV1Response<ConnectorTestResult>>(paths.autodiscover.connectorTest(id), { method: 'POST' })
    return unwrapConnectorTest(response)
  },
  syncConnector: async (id: number) => {
    const response = await api<ConnectorSyncV1Response<ConnectorSyncResult>>(paths.autodiscover.connectorSync(id), { method: 'POST' })
    return unwrapConnectorSync(response)
  },
  scan: async (body: AutodiscoverScanRequest) => {
    const response = await api<ScanV1Response<AutodiscoverScanResponse>>(paths.autodiscover.scan, {
      method: 'POST',
      body: JSON.stringify(body),
    })
    return unwrapScan(response)
  },
  getRun: async (runId: number) => {
    const response = await api<ScanV1Response>(paths.autodiscover.run(runId))
    return unwrapScan(response)
  },
  apply: async (runId: number, mappingIds?: string[]) => {
    const response = await api<ApplyV1Response<AutodiscoverApplyResponse>>(paths.autodiscover.apply(runId), {
      method: 'POST',
      body: JSON.stringify({ mapping_ids: mappingIds ?? null }),
    })
    return unwrapApply(response)
  },
}
