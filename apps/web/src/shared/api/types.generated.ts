/** AUTO-GENERATED — do not edit. Run: npm run codegen:api */

export type CIResponse = {
  id: number
  name: string
  type?: string | null
  type_id: number
  description?: string | null
  status: string
  criticality?: string | null
  environment?: string | null
  owner?: string | null
  team?: string | null
  attributes?: Record<string, unknown>
  external_ids?: Record<string, unknown>
  last_changed_at?: string | null
  created_at?: string | null
}

export type CIDetailResponse = {
  id: number
  name: string
  type?: string | null
  type_id: number
  description?: string | null
  status: string
  criticality?: string | null
  environment?: string | null
  owner?: string | null
  team?: string | null
  attributes?: Record<string, unknown>
  external_ids?: Record<string, unknown>
  last_changed_at?: string | null
  created_at?: string | null
  relations?: Record<string, unknown> | null
}

export type CIListResponse = {
  items: Array<CIResponse>
  total: number
  skip: number
  limit: number
}

export type RelationResponse = {
  id: number
  source_ci_id: number
  target_ci_id: number
  source_name?: string | null
  target_name?: string | null
  relation_type: string
  status: string
  data_source?: string | null
  direction: string
  created_at?: string | null
  last_changed_at?: string | null
}

export type AuditLogResponse = {
  id: number
  entity_type: string
  entity_id: number | null
  action: string
  user_email: string | null
  old_value: Record<string, unknown> | null
  new_value: Record<string, unknown> | null
  created_at?: string | null
}

export type AuditListResponse = {
  items: Array<AuditLogResponse>
  total: number
  skip: number
  limit: number
}

export type RelationValidationResponse = {
  valid: boolean
  issues: Array<Record<string, unknown>>
  issue_count: number
}

export type UserResponse = {
  email: string
  role: string
  is_active: boolean
  must_change_password?: boolean
}

export type ImportReport = {
  created?: number
  updated?: number
  skipped?: number
  errors?: Array<string>
}

export type DashboardModelHealth = {
  valid: boolean
  issue_count: number
}

export type DashboardOverviewResponse = {
  total_ci: number
  total_relations: number
  by_status: Record<string, number>
  by_type: Record<string, number>
  model_health: DashboardModelHealth
  recent_audit: Array<AuditLogResponse>
}

export type ImpactedServiceItem = {
  id: number
  name: string
  criticality?: string | null
}

export type ImpactResponse = {
  ci_id: number
  impacted_business_services: Array<ImpactedServiceItem>
  count: number
}

export type ComponentsResponse = {
  ci_id: number
  components: Array<CIResponse>
  count: number
}

export type BusinessPathResponse = {
  path: Array<CIResponse>
}

export type GraphLayoutPosition = {
  x: number
  y: number
}

export type GraphLayoutResponse = {
  root_ci_id: number
  relation_filter?: string
  positions?: Record<string, GraphLayoutPosition>
}

export type GraphNodeResponse = {
  id: number
  name: string
  type?: string | null
  type_id: number
  description?: string | null
  status: string
  criticality?: string | null
  environment?: string | null
  owner?: string | null
  team?: string | null
  attributes?: Record<string, unknown>
  external_ids?: Record<string, unknown>
  last_changed_at?: string | null
  created_at?: string | null
  depth?: number
}

export type GraphDataResponse = {
  nodes?: Array<GraphNodeResponse>
  edges?: Array<RelationResponse>
}

export type CorrelationMatchResult = {
  alert: Record<string, unknown>
  resolved: boolean
  ambiguous?: boolean
  resource?: CIResponse | null
  match_count?: number | null
}

export type CorrelationResolvePayload = {
  resolved: Array<CorrelationMatchResult>
  unresolved: Array<CorrelationMatchResult>
  schema_version: string
  pagination?: Record<string, number> | null
}

export type CorrelationEnrichmentItem = {
  resource_id: number
  name: string
  type?: string | null
  criticality?: string | null
  environment?: string | null
  owner?: string | null
  team?: string | null
  external_ids?: Record<string, unknown>
  impacted_services?: Array<Record<string, unknown>>
}

export type CorrelationContextPayload = {
  resource_ids?: Array<number>
  chain_related?: boolean
  chain_algorithm?: string
  graph?: GraphDataResponse
  direct_relations?: Array<RelationResponse>
  potential_root_cause_zone?: Array<CIResponse>
  enrichment?: Array<CorrelationEnrichmentItem>
}

export type CorrelationContextResponse = {
  schema_version: string
  correlation: CorrelationContextPayload
}

export type CorrelationIngestResponse = {
  source?: string | null
  schema_version: string
  resolve: CorrelationResolvePayload
  correlation?: CorrelationContextPayload
  enrichment?: Array<CorrelationEnrichmentItem>
  potential_root_cause_zone?: Array<CIResponse>
  webhook?: Record<string, unknown> | null
}

export type ResourceGraphResponse = {
  root_id: number
  depth: number
  nodes: Array<GraphNodeResponse>
  edges: Array<RelationResponse>
}
