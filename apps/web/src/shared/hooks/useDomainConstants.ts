import { useQuery } from '@tanstack/react-query'
import { useMemo } from 'react'
import { useAuth } from '@/context/useAuth'
import { miscApi } from '@/shared/api'
import type { DomainConstants } from '@/shared/api/types'
import {
  BULK_CI_STATUSES,
  CI_STATUSES,
  CRITICALITY_LEVELS,
  ENVIRONMENTS,
  RELATION_STATUSES,
  RELATION_TYPES,
  ROLES,
  RSM_OFFICIAL_TYPE_NAMES,
} from '@/shared/constants'
import { EXTERNAL_ID_FIELDS } from '@/shared/domainConstants.generated'
import { queryKeys } from '@/shared/queryKeys'

const FALLBACK: DomainConstants = {
  relation_types: [...RELATION_TYPES],
  relation_statuses: [...RELATION_STATUSES],
  ci_statuses: [...CI_STATUSES],
  criticality_levels: [...CRITICALITY_LEVELS],
  environments: [...ENVIRONMENTS],
  external_id_fields: [...EXTERNAL_ID_FIELDS],
  roles: [...ROLES],
  rsm_official_type_names: [...RSM_OFFICIAL_TYPE_NAMES],
}

export function useDomainConstants() {
  const { user } = useAuth()
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.meta.constants,
    queryFn: () => miscApi.constants(),
    enabled: !!user,
    staleTime: Infinity,
  })

  return useMemo(
    () => ({
      isLoading: !!user && isLoading,
      relationTypes: data?.relation_types ?? FALLBACK.relation_types,
      relationStatuses: data?.relation_statuses ?? FALLBACK.relation_statuses,
      ciStatuses: data?.ci_statuses ?? FALLBACK.ci_statuses,
      bulkCiStatuses: BULK_CI_STATUSES,
      criticalityLevels: data?.criticality_levels ?? FALLBACK.criticality_levels,
      environments: data?.environments ?? FALLBACK.environments,
      externalIdFields: data?.external_id_fields ?? [...EXTERNAL_ID_FIELDS],
      roles: data?.roles ?? FALLBACK.roles,
      rsmOfficialTypeNames: data?.rsm_official_type_names ?? FALLBACK.rsm_official_type_names,
    }),
    [data, isLoading, user],
  )
}
