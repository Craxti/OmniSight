import { describe, expect, it, vi } from 'vitest'
import { renderAppHook } from '@/test/renderHookWithProviders'
import { useRelationsPage } from '@/features/relations/hooks/useRelationsPage'

vi.mock('@/context/useAuth', () => ({
  useAuth: () => ({ canEdit: true }),
}))

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({
    t: {
      relations: {},
      common: { create: 'Create', save: 'Save', cancel: 'Cancel', error: 'Error' },
    },
    dateLocale: 'en',
  }),
}))

vi.mock('@/shared/hooks/useCiList', () => ({
  useCiList: () => ({ data: { items: [] } }),
}))

vi.mock('@/shared/hooks/useRelationValidation', () => ({
  useRelationValidation: () => ({ validation: null, validate: vi.fn() }),
}))

vi.mock('@/shared/api', () => ({
  relationsApi: {
    listPage: vi.fn().mockResolvedValue({
      items: [],
      pagination: { page: 1, page_size: 50, total_items: 0, total_pages: 1 },
    }),
  },
  miscApi: { entityAudit: vi.fn().mockResolvedValue([]) },
}))

vi.mock('@/features/relations/hooks/useRelationsMutations', () => ({
  useRelationsMutations: () => ({
    createMut: { mutate: vi.fn(), isPending: false },
    deleteMut: { mutate: vi.fn(), isPending: false },
    updateMut: { mutate: vi.fn(), isPending: false },
    bulkMut: { mutate: vi.fn(), isPending: false },
    bulkDeleteMut: { mutate: vi.fn(), isPending: false },
    invalidate: vi.fn(),
  }),
}))

describe('useRelationsPage', () => {
  it('starts on page 1 with create form closed', () => {
    const { result } = renderAppHook(() => useRelationsPage())
    expect(result.current.showForm).toBe(false)
    expect(result.current.page).toBe(1)
  })

  it('loads relations from paginated API with default empty filters', () => {
    const { result } = renderAppHook(() => useRelationsPage())
    expect(result.current.relations).toEqual([])
    expect(result.current.page).toBe(1)
  })
})
