import { useQuery } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { useCiList } from '@/shared/hooks/useCiList'
import { useDebouncedValue } from '@/shared/hooks/useDebouncedValue'
import { useEntityListPageState } from '@/shared/hooks/useEntityListPageState'
import { useRelationValidation } from '@/shared/hooks/useRelationValidation'
import { miscApi, relationsApi } from '@/shared/api'
import { omitFalsyValues } from '@/shared/api/v1Envelope'
import { queryKeys } from '@/shared/queryKeys'
import { defaultRelationsFilters, type RelationsFilterState } from '@/features/relations/relationsFilters'
import { defaultRelationForm } from '@/features/relations/relationsForm'
import { useRelationsMutations } from '@/features/relations/hooks/useRelationsMutations'
import { useIdSelection } from '@/shared/hooks/useIdSelection'

const PAGE_SIZE = 50

function activeFilterParams(filters: RelationsFilterState) {
  return omitFalsyValues(filters)
}

export function useRelationsPage() {
  const { canEdit } = useAuth()
  const { t, dateLocale } = useI18n()
  const {
    filters,
    setFilters: setFiltersState,
    showForm,
    setShowForm,
    importReport,
    setImportReport,
  } = useEntityListPageState({ filters: defaultRelationsFilters, form: defaultRelationForm })
  const [page, setPage] = useState(1)
  const debouncedFilters = useDebouncedValue(filters, 300)
  const [auditRelId, setAuditRelId] = useState<number | null>(null)
  const [editRel, setEditRel] = useState<{
    id: number
    relation_type: string
    status: string
    data_source: string
  } | null>(null)

  const activeFilters = useMemo(() => activeFilterParams(debouncedFilters), [debouncedFilters])

  useEffect(() => {
    setPage(1)
  }, [debouncedFilters])

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.relations.list(activeFilters, page),
    queryFn: () => relationsApi.listPage({ page, page_size: PAGE_SIZE, ...activeFilters }),
    placeholderData: (prev) => prev,
  })
  const { data: cis } = useCiList()
  const { validation, validate, validating } = useRelationValidation()
  const { data: relAudit } = useQuery({
    queryKey: queryKeys.relations.audit(auditRelId!),
    queryFn: () => miscApi.entityAudit('relation', auditRelId!),
    enabled: auditRelId !== null,
  })

  const relations = data?.items ?? []
  const pagination = data?.pagination
  const totalPages = pagination?.total_pages ?? 1
  const { selected, toggleAll, toggleOne, clearSelection } = useIdSelection(relations.map((r) => r.id))

  const { createMut, deleteMut, updateMut, bulkMut, bulkDeleteMut, invalidate } = useRelationsMutations(t, {
    selected,
    onCreateSuccess: () => setShowForm(false),
    onUpdateSuccess: () => setEditRel(null),
    onBulkSuccess: clearSelection,
  })

  return {
    canEdit,
    t,
    dateLocale,
    showForm,
    setShowForm,
    auditRelId,
    setAuditRelId,
    importReport,
    setImportReport,
    filters,
    setFilters: setFiltersState,
    editRel,
    setEditRel,
    relations,
    isLoading,
    cis,
    validation,
    validate,
    validating,
    relAudit,
    createMut,
    deleteMut,
    updateMut,
    bulkMut,
    bulkDeleteMut,
    invalidate,
    selected,
    toggleAll,
    toggleOne,
    page,
    setPage,
    totalPages,
    totalItems: pagination?.total_items ?? 0,
  }
}
