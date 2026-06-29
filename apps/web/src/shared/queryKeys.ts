export const queryKeys = {
  meta: {
    constants: ['meta-constants'] as const,
  },
  autodiscover: {
    profiles: ['autodiscover-profiles'] as const,
    connectors: ['autodiscover-connectors'] as const,
  },
  ci: {
    all: ['ci'] as const,
    list: (filters: unknown, view: unknown, page?: number, pageSize?: number) =>
      ['ci', filters, view, page ?? 1, pageSize ?? 50] as const,
    detail: (id: number | string) => ['ci', id] as const,
    recycle: ['ci-recycle'] as const,
    allList: (limit: number) => ['ci-all', limit] as const,
    types: ['ci-types'] as const,
    businessServices: (typeId: number | undefined) => ['ci-business-services', typeId] as const,
    relations: (ciId: number | string) => ['ci-relations', ciId] as const,
    components: (ciId: number | string) => ['components', ciId] as const,
    audit: (ciId: number | string) => ['audit-ci', ciId] as const,
  },
  relations: {
    all: ['relations'] as const,
    relationTypes: ['relation-types'] as const,
    list: (filters: unknown, page: number) => ['relations', 'list', filters, page] as const,
    validate: ['relations-validate'] as const,
    audit: (id: number | string) => ['audit-relation', id] as const,
  },
  users: ['users'] as const,
  dashboard: ['dashboard'] as const,
  audit: {
    all: ['audit'] as const,
    list: (params: unknown) => ['audit', params] as const,
  },
  search: (q: string) => ['search', q] as const,
  graph: (id: number | string, depth: number) => ['graph', id, depth] as const,
  graphLayout: (id: number | string, relationFilter: string) => ['graph-layout', id, relationFilter] as const,
  businessPath: (id: number | string) => ['business-path', id] as const,
  impact: (id: number | string) => ['impact', id] as const,
} as const
