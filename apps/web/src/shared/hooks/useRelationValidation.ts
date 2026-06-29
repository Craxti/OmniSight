import { useQuery } from '@tanstack/react-query'
import { relationsApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

/** Shared relation model validation query (cache key deduplicated across pages). */
export function useRelationValidation() {
  const { data: validation, refetch: validate, isFetching: validating } = useQuery({
    queryKey: queryKeys.relations.validate,
    queryFn: relationsApi.validate,
    enabled: false,
  })

  return { validation, validate, validating }
}
