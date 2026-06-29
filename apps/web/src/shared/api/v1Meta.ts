import type { DomainConstants } from '@/shared/api/types'
import { type V1Base, unwrapV1Field } from '@/shared/api/v1Envelope'

export const META_SCHEMA_V1 = 'rsm-meta-v1' as const

export type DomainConstantsV1Response = V1Base & {
  constants: DomainConstants
}

export const unwrapDomainConstants = (body: DomainConstantsV1Response) => unwrapV1Field(body, 'constants')
