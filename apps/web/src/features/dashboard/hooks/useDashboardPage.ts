import { useQuery } from '@tanstack/react-query'
import { miscApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

export function useDashboardPage() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: () => miscApi.dashboard(),
    placeholderData: (prev) => prev,
  })
}
