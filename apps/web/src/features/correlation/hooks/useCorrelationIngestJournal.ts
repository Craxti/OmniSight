import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { correlationApi } from '@/shared/api'
import { queryKeys } from '@/shared/queryKeys'

export const INGEST_JOURNAL_PAGE_SIZE = 15
const REFRESH_MS = 5000

export function useCorrelationIngestJournal() {
  const [page, setPage] = useState(0)
  const [sourceFilter, setSourceFilter] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const listParams = useMemo(
    () => ({
      page: page + 1,
      page_size: INGEST_JOURNAL_PAGE_SIZE,
      ...(sourceFilter.trim() ? { source: sourceFilter.trim() } : {}),
    }),
    [page, sourceFilter],
  )

  const listQuery = useQuery({
    queryKey: queryKeys.correlation.ingestLogs(listParams),
    queryFn: () => correlationApi.ingestLogs(listParams),
    refetchInterval: REFRESH_MS,
    placeholderData: (prev) => prev,
  })

  const detailQuery = useQuery({
    queryKey: queryKeys.correlation.ingestLog(selectedId),
    queryFn: () => correlationApi.ingestLog(selectedId!),
    enabled: selectedId != null,
  })

  const items = listQuery.data?.items ?? []
  const total = listQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / INGEST_JOURNAL_PAGE_SIZE))

  const openLog = (id: number) => setSelectedId(id)

  const closeLog = () => setSelectedId(null)

  const resetPage = () => setPage(0)

  return {
    page,
    setPage,
    sourceFilter,
    setSourceFilter,
    resetPage,
    selectedId,
    openLog,
    closeLog,
    setSelectedId,
    items,
    total,
    totalPages,
    stats: listQuery.data?.stats ?? null,
    isLoading: listQuery.isLoading,
    isDetailLoading: detailQuery.isLoading,
    detail: detailQuery.data ?? null,
    refetch: listQuery.refetch,
  }
}
