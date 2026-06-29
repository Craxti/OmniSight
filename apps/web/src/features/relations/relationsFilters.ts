export type RelationsFilterState = {
  q: string
  relation_type: string
  status: string
  data_source: string
  source_name: string
  target_name: string
}

export const defaultRelationsFilters: RelationsFilterState = {
  q: '',
  relation_type: '',
  status: '',
  data_source: '',
  source_name: '',
  target_name: '',
}
