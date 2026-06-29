import { useQuery } from '@tanstack/react-query'
import { ciApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

export const CI_TYPES_QUERY_KEY = queryKeys.ci.types

export function useCiTypes(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.ci.types,
    queryFn: ciApi.types,
    enabled: options?.enabled ?? true,
  })
}
