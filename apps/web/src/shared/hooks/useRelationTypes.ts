import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { mergeRelationTypes } from '@/lib/relationTypeCatalog'
import { relationTypesApi } from '@/shared/api/relationTypes'
import { queryKeys } from '@/shared/queryKeys'

export function useRelationTypes(options?: { enabled?: boolean }) {
  const query = useQuery({
    queryKey: queryKeys.relations.relationTypes,
    queryFn: relationTypesApi.list,
    enabled: options?.enabled ?? true,
  })

  const data = useMemo(() => mergeRelationTypes(query.data), [query.data])

  return { ...query, data }
}
