import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useI18n } from '@/context/useI18n'
import { miscApi } from '@/shared/api'
import type { AuditEntry } from '@/shared/api/types'
import { queryKeys } from '@/shared/queryKeys'

export const AUDIT_PAGE_SIZE = 25

export function useAuditPage() {
  const { t, dateLocale } = useI18n()
  const [entityType, setEntityType] = useState('')
  const [action, setAction] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [page, setPage] = useState(0)

  const params = useMemo(() => {
    const next: Record<string, string> = {
      skip: String(page * AUDIT_PAGE_SIZE),
      limit: String(AUDIT_PAGE_SIZE),
    }
    if (entityType) next.entity_type = entityType
    if (action) next.action = action
    if (userEmail.trim()) next.user_email = userEmail.trim()
    if (dateFrom) next.date_from = dateFrom
    if (dateTo) next.date_to = dateTo
    return next
  }, [entityType, action, userEmail, dateFrom, dateTo, page])

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.audit.list(params),
    queryFn: () => miscApi.audit(params),
  })

  const items: AuditEntry[] = data?.items ?? []
  const total = data?.total || 0
  const totalPages = Math.max(1, Math.ceil(total / AUDIT_PAGE_SIZE))

  const resetPage = () => setPage(0)

  return {
    t,
    dateLocale,
    entityType,
    setEntityType,
    action,
    setAction,
    userEmail,
    setUserEmail,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    page,
    setPage,
    resetPage,
    isLoading,
    items,
    total,
    totalPages,
  }
}
