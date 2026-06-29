import { EnvironmentInput } from '@/shared/components/EnvironmentInput'
import { useI18n } from '@/context/useI18n'
import {
  CompactFilterPanel,
  FilterAdvancedGrid,
  FilterAdvancedToggle,
  FilterClearButton,
  FilterSelect,
  FilterTextInput,
  FilterToolbar,
  FilterToolbarSearch,
  hasAnyFilter,
  useFilterAdvancedSection,
} from '@/shared/components/FilterPanel'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { ciStatusLabel } from '@/lib/domainLabels'
import { defaultInventoryFilters, type InventoryFilterState } from '@/features/inventory/inventoryFilters'
export type { InventoryFilterState } from '@/features/inventory/inventoryFilters'

const ADVANCED_KEYS = ['environment', 'owner', 'hostname', 'external_id'] as const

interface InventoryFiltersProps {
  filters: InventoryFilterState
  types?: Array<{ id: number; name: string }>
  onChange: (filters: InventoryFilterState) => void
}

export function InventoryFilters({ filters, types, onChange }: InventoryFiltersProps) {
  const { t } = useI18n()
  const { ciStatuses } = useDomainConstants()
  const { expanded, toggle, advancedActiveCount } = useFilterAdvancedSection(ADVANCED_KEYS, filters)

  const set = (patch: Partial<InventoryFilterState>) => onChange({ ...filters, ...patch })

  return (
    <CompactFilterPanel>
      <FilterToolbar>
        <FilterToolbarSearch
          value={filters.q}
          placeholder={t.inventory.searchQ}
          testId="inventory-filter-q"
          onChange={(q) => set({ q })}
        />
        <FilterSelect
          value={filters.type_id}
          data-testid="inventory-filter-type"
          aria-label={t.inventory.allTypes}
          onChange={(e) => set({ type_id: e.target.value })}
        >
          <option value="">{t.inventory.allTypes}</option>
          {(types || []).map((typeOpt) => (
            <option key={typeOpt.id} value={typeOpt.id}>
              {typeOpt.name}
            </option>
          ))}
        </FilterSelect>
        <FilterSelect
          value={filters.status}
          aria-label={t.inventory.allStatuses}
          onChange={(e) => set({ status: e.target.value })}
        >
          <option value="">{t.inventory.allStatuses}</option>
          {ciStatuses.map((s) => (
            <option key={s} value={s}>
              {ciStatusLabel(t, s)}
            </option>
          ))}
        </FilterSelect>
        <FilterAdvancedToggle
          expanded={expanded}
          activeCount={advancedActiveCount}
          moreLabel={t.common.moreFilters}
          hideLabel={t.common.hideFilters}
          onToggle={toggle}
        />
        <FilterClearButton
          visible={hasAnyFilter(filters)}
          label={t.common.clearFilters}
          onClick={() => onChange(defaultInventoryFilters)}
        />
      </FilterToolbar>
      <FilterAdvancedGrid open={expanded}>
        <EnvironmentInput
          id="inventory-filter-env"
          value={filters.environment}
          onChange={(environment) => set({ environment })}
          placeholder={t.inventory.allEnvironments}
          data-testid="inventory-filter-environment"
          allowEmpty
        />
        <FilterTextInput
          value={filters.owner}
          placeholder={t.inventory.filterOwner}
          testId="inventory-filter-owner"
          onChange={(owner) => set({ owner })}
        />
        <FilterTextInput
          value={filters.hostname}
          placeholder={t.inventory.filterHostname}
          testId="inventory-filter-hostname"
          onChange={(hostname) => set({ hostname })}
        />
        <FilterTextInput
          value={filters.external_id}
          placeholder={t.inventory.filterExternalId}
          testId="inventory-filter-external-id"
          onChange={(external_id) => set({ external_id })}
        />
      </FilterAdvancedGrid>
    </CompactFilterPanel>
  )
}
