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
import { useI18n } from '@/context/useI18n'
import { relationStatusLabel, relationTypeLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { defaultRelationsFilters, type RelationsFilterState } from '@/features/relations/relationsFilters'
export type { RelationsFilterState } from '@/features/relations/relationsFilters'
export { defaultRelationsFilters } from '@/features/relations/relationsFilters'

const ADVANCED_KEYS = ['data_source', 'source_name', 'target_name'] as const

interface RelationsFiltersProps {
  filters: RelationsFilterState
  onChange: (filters: RelationsFilterState) => void
}

export function RelationsFilters({ filters, onChange }: RelationsFiltersProps) {
  const { t } = useI18n()
  const { relationTypes, relationStatuses } = useDomainConstants()
  const { expanded, toggle, advancedActiveCount } = useFilterAdvancedSection(ADVANCED_KEYS, filters)

  const set = (patch: Partial<RelationsFilterState>) => onChange({ ...filters, ...patch })

  return (
    <CompactFilterPanel testId="relations-filters">
      <FilterToolbar>
        <FilterToolbarSearch
          value={filters.q}
          placeholder={t.relations.searchQ}
          testId="relations-filter-q"
          onChange={(q) => set({ q })}
        />
        <FilterSelect
          value={filters.relation_type}
          data-testid="relations-filter-type"
          aria-label={t.relations.allRelationTypes}
          onChange={(e) => set({ relation_type: e.target.value })}
        >
          <option value="">{t.relations.allRelationTypes}</option>
          {relationTypes.map((rt) => (
            <option key={rt} value={rt}>
              {relationTypeLabel(t, rt)}
            </option>
          ))}
        </FilterSelect>
        <FilterSelect
          value={filters.status}
          data-testid="relations-filter-status"
          aria-label={t.relations.allStatuses}
          onChange={(e) => set({ status: e.target.value })}
        >
          <option value="">{t.relations.allStatuses}</option>
          {relationStatuses.map((s) => (
            <option key={s} value={s}>
              {relationStatusLabel(t, s)}
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
          onClick={() => onChange(defaultRelationsFilters)}
        />
      </FilterToolbar>
      <FilterAdvancedGrid open={expanded}>
        <FilterTextInput
          value={filters.data_source}
          placeholder={t.relations.filterDataSource}
          testId="relations-filter-data-source"
          onChange={(data_source) => set({ data_source })}
        />
        <FilterTextInput
          value={filters.source_name}
          placeholder={t.relations.filterSource}
          testId="relations-filter-source"
          onChange={(source_name) => set({ source_name })}
        />
        <FilterTextInput
          value={filters.target_name}
          placeholder={t.relations.filterTarget}
          testId="relations-filter-target"
          onChange={(target_name) => set({ target_name })}
        />
      </FilterAdvancedGrid>
    </CompactFilterPanel>
  )
}
