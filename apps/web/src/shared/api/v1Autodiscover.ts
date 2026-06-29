import {
  type V1Base,
  type V1Pagination,
  unwrapV1Field,
  unwrapV1Items,
} from '@/shared/api/v1Envelope'
import { type DeleteResultV1Response, unwrapDeleteResult } from '@/shared/api/v1Inventory'

export const AUTODISCOVER_SCHEMA_V1 = 'rsm-autodiscover-v1' as const

export type AutodiscoverItemsV1Response<T> = V1Base & {
  items: T[]
  pagination: V1Pagination
}

export type ConnectorV1Response<T = unknown> = V1Base & {
  connector: T
}

export type ScanV1Response<T = unknown> = V1Base & {
  scan: T
}

export type ApplyV1Response<T = unknown> = V1Base & {
  apply: T
}

export type ConnectorTestV1Response<T = unknown> = V1Base & {
  test: T
}

export type ConnectorSyncV1Response<T = unknown> = V1Base & {
  sync: T
}

export function unwrapAutodiscoverItems<T>(body: AutodiscoverItemsV1Response<T>): T[] {
  return unwrapV1Items(body)
}

export function unwrapConnector<T>(body: ConnectorV1Response<T>): T {
  return unwrapV1Field(body, 'connector')
}

export function unwrapScan<T>(body: ScanV1Response<T>): T {
  return unwrapV1Field(body, 'scan')
}

export function unwrapApply<T>(body: ApplyV1Response<T>): T {
  return unwrapV1Field(body, 'apply')
}

export function unwrapConnectorTest<T>(body: ConnectorTestV1Response<T>): T {
  return unwrapV1Field(body, 'test')
}

export function unwrapConnectorSync<T>(body: ConnectorSyncV1Response<T>): T {
  return unwrapV1Field(body, 'sync')
}

export { unwrapDeleteResult, type DeleteResultV1Response }
