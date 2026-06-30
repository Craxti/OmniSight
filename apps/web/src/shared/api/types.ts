import type { components } from '@/shared/api/generated/schema'
import type {
  AuditListResponse,
  AuditLogResponse,
  BusinessPathResponse as ApiBusinessPathResponse,
  CIListResponse,
  CIDetailResponse,
  CIResponse,
  ComponentsResponse as ApiComponentsResponse,
  CorrelationContextPayload as ApiCorrelationContextPayload,
  CorrelationContextResponse as ApiCorrelationContextResponse,
  CorrelationEnrichmentItem as ApiCorrelationEnrichmentItem,
  CorrelationIngestResponse as ApiCorrelationIngestResponse,
  CorrelationMatchResult,
  CorrelationResolvePayload,
  DashboardOverviewResponse,
  GraphLayoutResponse as ApiGraphLayoutResponse,
  GraphNodeResponse,
  ImpactResponse as ApiImpactResponse,
  RelationResponse,
  RelationValidationResponse,
  UserResponse,
} from '@/shared/api/types.generated'

type Schemas = components['schemas']

/** Frontend aliases — generated from Pydantic via `npm run codegen:api`. */
export type CI = CIResponse
export type CIDetail = CIDetailResponse
export type CIList = CIListResponse
export type Relation = RelationResponse
export type UserInfo = UserResponse
export type AuditEntry = AuditLogResponse
export type RelationValidationResult = RelationValidationResponse
export type CorrelationMatch = CorrelationMatchResult
export type CorrelationResolveResponse = CorrelationResolvePayload
export type DashboardData = DashboardOverviewResponse
export type GraphNode = Omit<GraphNodeResponse, 'depth'> & { depth?: number }
export type GraphEdge = RelationResponse
export type GraphData = {
  root_id?: number
  depth?: number
  nodes: GraphNode[]
  edges: GraphEdge[]
}

/** Nodes/edges subset for correlation UI. */
export type GraphPanelData = {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export type RelationCreate = Schemas['RelationCreate']

export type ImportTypeDraft = Schemas['ImportTypeDraft']
export type ImportTypeMappingEntry = Schemas['ImportTypeMappingEntry']
export type ImportTypeProposal = Schemas['ImportTypeProposal']
export type ImportTypePreview = Omit<Schemas['ImportTypePreview'], 'existing_types'> & {
  existing_types: Array<{ id: number; name: string }>
}

export type { AuditListResponse }

export type ImportReport = {
  created: number
  updated: number
  skipped: number
  errors: string[]
}

export type CorrelationContextResponse = ApiCorrelationContextResponse
export type CorrelationIngestResponse = ApiCorrelationIngestResponse
export type CorrelationContextPayload = ApiCorrelationContextPayload
export type CorrelationEnrichmentItem = ApiCorrelationEnrichmentItem

export type CorrelationIngestLogSummary = {
  id: number
  source: string | null
  alert_count: number
  resolved_count: number
  unresolved_count: number
  chain_related: boolean
  created_at: string | null
}

export type CorrelationIngestLogDetail = CorrelationIngestLogSummary & {
  alerts: Record<string, string>[]
  result: CorrelationIngestResponse
}

export type BusinessPathResponse = ApiBusinessPathResponse
export type ImpactResponse = ApiImpactResponse
export type ComponentsResponse = ApiComponentsResponse
export type GraphLayoutResponse = ApiGraphLayoutResponse

export type DomainConstants = {
  relation_types: string[]
  relation_statuses: string[]
  ci_statuses: string[]
  criticality_levels: string[]
  environments: string[]
  external_id_fields: string[]
  roles: string[]
  rsm_official_type_names: string[]
}

export type { components, operations, paths } from '@/shared/api/generated/schema'
