import { DEFAULT_DATA_SOURCE, DEFAULT_RELATION_TYPE, type RelationType } from '@/shared/constants'

export type RelationFormState = {
  source_ci_id: string
  target_ci_id: string
  relation_type: RelationType
  data_source: typeof DEFAULT_DATA_SOURCE
}

export const defaultRelationForm: RelationFormState = {
  source_ci_id: '',
  target_ci_id: '',
  relation_type: DEFAULT_RELATION_TYPE,
  data_source: DEFAULT_DATA_SOURCE,
}
