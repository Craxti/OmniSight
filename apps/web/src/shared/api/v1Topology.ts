import type {
  BusinessPathResponse,
  ComponentsResponse,
  GraphData,
  GraphLayoutResponse,
  ImpactResponse,
} from '@/shared/api/types'
import { type V1Base, unwrapV1Field } from '@/shared/api/v1Envelope'

export const TOPOLOGY_SCHEMA_V1 = 'rsm-topology-v1' as const

export type GraphV1Response = V1Base & {
  graph: GraphData
}

export type ImpactV1Response = V1Base & {
  impact: ImpactResponse
}

export type ComponentsV1Response = V1Base & {
  components: ComponentsResponse
}

export type BusinessPathV1Response = V1Base & {
  business_path: BusinessPathResponse
}

export type GraphLayoutV1Response = V1Base & {
  layout: GraphLayoutResponse
}

export const unwrapGraph = (body: GraphV1Response) => unwrapV1Field(body, 'graph')
export const unwrapImpact = (body: ImpactV1Response) => unwrapV1Field(body, 'impact')
export const unwrapComponents = (body: ComponentsV1Response) => unwrapV1Field(body, 'components')
export const unwrapBusinessPath = (body: BusinessPathV1Response) => unwrapV1Field(body, 'business_path')
export const unwrapGraphLayout = (body: GraphLayoutV1Response) => unwrapV1Field(body, 'layout')
