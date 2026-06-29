import { useQuery } from '@tanstack/react-query'
import { useEffect } from 'react'
import { autodiscoverApi } from '@/shared/api/autodiscover'
import { ciApi } from '@/shared/api/ci'
import { SERVER_TYPE_NAME } from '@/shared/constants'
import { useCiTypes } from '@/shared/hooks/useCiTypes'
import { queryKeys } from '@/shared/queryKeys'

export function useAutodiscoverQueries(
  open: boolean,
  selectedServers: number[],
  setSelectedServers: (ids: number[] | ((prev: number[]) => number[])) => void,
) {
  const { data: profiles } = useQuery({
    queryKey: queryKeys.autodiscover.profiles,
    queryFn: () => autodiscoverApi.profiles(),
    enabled: open,
  })

  const { data: types } = useCiTypes({ enabled: open })
  const serverTypeId = types?.find((tp) => tp.name === SERVER_TYPE_NAME)?.id

  const { data: servers, isLoading: serversLoading } = useQuery({
    queryKey: [...queryKeys.ci.all, 'servers', serverTypeId],
    queryFn: () => ciApi.list({ type_id: serverTypeId!, limit: 200 }),
    enabled: open && !!serverTypeId,
  })

  const { data: connectors } = useQuery({
    queryKey: queryKeys.autodiscover.connectors,
    queryFn: () => autodiscoverApi.connectors(true),
    enabled: open,
  })

  useEffect(() => {
    if (!open || !servers?.items?.length || !connectors?.length) return
    const hostServerIds = connectors
      .filter((c) => c.enabled && c.connector_type === 'host' && c.server_ci_id)
      .map((c) => c.server_ci_id as number)
    if (hostServerIds.length > 0 && selectedServers.length === 0) {
      setSelectedServers([...new Set(hostServerIds)])
    }
  }, [open, servers, connectors, selectedServers.length, setSelectedServers])

  return { profiles, servers, serversLoading, connectors }
}
