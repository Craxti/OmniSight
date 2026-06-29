import type { UserInfo } from '@/shared/api/types'
import {
  type V1Base,
  type V1Pagination,
  unwrapV1Field,
  unwrapV1Items,
  unwrapV1Result,
} from '@/shared/api/v1Envelope'

export const AUTH_SCHEMA_V1 = 'rsm-auth-v1' as const

export type SessionV1Response = V1Base & {
  session: {
    access_token: string
    token_type?: string
    must_change_password?: boolean
  }
}

export type UserV1Response = V1Base & {
  user: UserInfo
}

export type AuthItemsV1Response<T = UserInfo> = V1Base & {
  items: T[]
  pagination: V1Pagination
}

export type AuthResultV1Response = V1Base & {
  result: { ok: boolean }
}

export const unwrapSession = (body: SessionV1Response) => unwrapV1Field(body, 'session')
export const unwrapUser = (body: UserV1Response) => unwrapV1Field(body, 'user')
export const unwrapAuthItems = unwrapV1Items
export const unwrapAuthResult = unwrapV1Result
