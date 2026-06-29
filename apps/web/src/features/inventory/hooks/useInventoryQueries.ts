import { useQuery } from '@tanstack/react-query'
import { ciApi, type CI } from '@/shared/api'
import { omitFalsyValues } from '@/shared/api/v1Envelope'
import { BUSINESS_SERVICE_TYPE_NAME } from '@/shared/constants'
import { useCiTypes } from '@/shared/hooks/useCiTypes'
import { queryKeys } from '@/shared/queryKeys'
import type { InventoryFilterState } from '@/features/inventory/inventoryFilters'

export const INVENTORY_PAGE_SIZE_DEFAULT = 50
export const INVENTORY_PAGE_SIZES = [50, 100, 200] as const
export type InventoryPageSize = (typeof INVENTORY_PAGE_SIZES)[number]

export function useInventoryQueries(
  view: 'active' | 'recycle',
  filters: InventoryFilterState,
  page: number,
  pageSize: InventoryPageSize,
) {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.ci.list(filters, view, page, pageSize),
    queryFn: () =>
      ciApi.listPage({
        page,
        page_size: pageSize,
        ...omitFalsyValues(filters),
      }),
    enabled: view === 'active',
    placeholderData: (prev) => prev,
  })

  const { data: recycled, isLoading: loadingBin } = useQuery({
    queryKey: queryKeys.ci.recycle,
    queryFn: ciApi.recycleBin,
    enabled: view === 'recycle',
  })

  const { data: types } = useCiTypes()

  const businessServiceTypeId = types?.find((tp) => tp.name === BUSINESS_SERVICE_TYPE_NAME)?.id
  const { data: businessServicesData } = useQuery({
    queryKey: queryKeys.ci.businessServices(businessServiceTypeId),
    queryFn: () => ciApi.list({ type_id: businessServiceTypeId!, limit: 500 }),
    enabled: !!businessServiceTypeId,
  })

  const businessServices = (businessServicesData?.items || []).map((c) => ({ id: c.id, name: c.name }))
  const items: CI[] = view === 'active' ? (data?.items || []) : (recycled || [])
  const pagination = data?.pagination
  const totalItems = view === 'active' ? (pagination?.total_items ?? 0) : items.length
  const totalPages = view === 'active' ? (pagination?.total_pages ?? 1) : 1

  return {
    items,
    isLoading: isLoading || loadingBin,
    types,
    businessServices,
    totalItems,
    totalPages,
  }
}
