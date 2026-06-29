import { useQuery } from '@tanstack/react-query'
import { resourcesApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

type Options = {
  businessPath?: boolean
  impact?: boolean
  components?: boolean
  isBusinessService?: boolean
}

export function useCiResourcePanels(ciId: number, options: Options = {}) {
  const { businessPath = false, impact = false, components = false, isBusinessService = false } = options

  const businessPathQuery = useQuery({
    queryKey: queryKeys.businessPath(ciId),
    queryFn: () => resourcesApi.businessPath(ciId),
    enabled: businessPath && !!ciId,
  })

  const impactQuery = useQuery({
    queryKey: queryKeys.impact(ciId),
    queryFn: () => resourcesApi.impact(ciId),
    enabled: impact && !!ciId,
  })

  const componentsQuery = useQuery({
    queryKey: queryKeys.ci.components(ciId),
    queryFn: () => resourcesApi.components(ciId),
    enabled: components && !!ciId && isBusinessService,
  })

  return {
    businessPath: businessPathQuery.data,
    impact: impactQuery.data,
    components: componentsQuery.data,
    isLoading:
      (businessPath && businessPathQuery.isLoading) ||
      (impact && impactQuery.isLoading) ||
      (components && componentsQuery.isLoading),
  }
}
