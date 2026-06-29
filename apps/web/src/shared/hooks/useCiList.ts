import { useQuery } from '@tanstack/react-query'
import { ciApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

export function useCiList(limit = 200) {
  return useQuery({
    queryKey: queryKeys.ci.allList(limit),
    queryFn: () => ciApi.list({ limit }),
  })
}
