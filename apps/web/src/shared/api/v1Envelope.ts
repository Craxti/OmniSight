/** Shared v1 API envelope types and helpers. */

export type V1Pagination = {
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export type V1Base = {
  api_version: 'v1'
  schema_version: string
}

/** Map skip/limit query params to v1 page/page_size. */
export function toV1ListParams(params?: Record<string, string | number>) {
  const { skip, limit, ...rest } = params ?? {}
  const page_size = Math.min(500, Math.max(1, Number(limit ?? 50)))
  const page =
    skip != null && Number.isFinite(Number(skip))
      ? Math.floor(Number(skip) / page_size) + 1
      : 1
  return { page, page_size, ...rest }
}

/** Omit object entries with falsy values (used for filter/query params). */
export function omitFalsyValues<T extends Record<string, unknown>>(obj: T): Partial<T> {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => v)) as Partial<T>
}

/** @deprecated Use `omitFalsyValues` — omits all falsy values (0, false, '', null, undefined). */
export const omitFalsy = omitFalsyValues

export { omitBlank, omitEmpty } from '@/shared/api/client'

export function unwrapV1Field<T, K extends string>(body: V1Base & Record<K, T>, key: K): T {
  return body[key]
}

export function unwrapV1Items<T>(body: V1Base & { items: T[]; pagination?: V1Pagination }): T[] {
  return body.items
}

export function unwrapV1ListTotal<T>(body: V1Base & { items: T[]; pagination: V1Pagination }) {
  return { items: body.items, total: body.pagination.total_items }
}

export function unwrapV1PagedItems<T>(body: V1Base & { items: T[]; pagination: V1Pagination }) {
  return body
}

export function unwrapV1Result(body: V1Base & { result: { ok: boolean } }) {
  return body.result
}

export function unwrapV1Ci<T>(body: V1Base & { ci: T }): T {
  return unwrapV1Field(body, 'ci')
}

export function unwrapV1Relation<T>(body: V1Base & { relation: T }): T {
  return unwrapV1Field(body, 'relation')
}

export function unwrapV1Connector<T>(body: V1Base & { connector: T }): T {
  return unwrapV1Field(body, 'connector')
}

export function unwrapV1Scan<T>(body: V1Base & { scan: T }): T {
  return unwrapV1Field(body, 'scan')
}

export function unwrapV1Apply<T>(body: V1Base & { apply: T }): T {
  return unwrapV1Field(body, 'apply')
}

export function unwrapV1Test<T>(body: V1Base & { test: T }): T {
  return unwrapV1Field(body, 'test')
}

export function unwrapV1Sync<T>(body: V1Base & { sync: T }): T {
  return unwrapV1Field(body, 'sync')
}
