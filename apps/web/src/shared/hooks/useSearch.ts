import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { resourcesApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

export function useSearch(query: string) {
  const [debounced, setDebounced] = useState('')

  useEffect(() => {
    if (query.length < 2) {
      setDebounced('')
      return
    }
    const timer = setTimeout(() => setDebounced(query), 200)
    return () => clearTimeout(timer)
  }, [query])

  return useQuery({
    queryKey: queryKeys.search(debounced),
    queryFn: async () => {
      const { items } = await resourcesApi.search({ q: debounced })
      return { cis: items }
    },
    enabled: debounced.length >= 2,
  })
}
