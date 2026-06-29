import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'
import { createHookWrapper, renderAppHook } from '@/test/renderHookWithProviders'
import { useGraphPage, useGraphPageState } from '@/features/graph/hooks/useGraphPage'

vi.mock('@/context/useAuth', () => ({
  useAuth: () => ({ canEdit: true }),
}))

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({ t: { graph: { toastExported: 'ok', toastExportError: 'err' } } }),
}))

vi.mock('@/context/useTheme', () => ({
  useTheme: () => ({ theme: 'light' }),
}))

vi.mock('@/context/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

vi.mock('@/features/graph/hooks/useGraphQueries', () => ({
  useGraphQueries: () => ({
    graph: { nodes: [{ id: 1, name: 'srv', type: 'Server' }], edges: [] },
    isLoading: false,
    businessPath: null,
    impact: null,
    components: null,
    pathIds: new Set<number>(),
    pathEdgeKeys: [],
    impactIds: new Set<number>(),
    componentIds: new Set<number>(),
    isBusinessServiceRoot: false,
    ciDisplay: (id: number) => `#${id}`,
  }),
}))

vi.mock('@/shared/hooks/useRelationValidation', () => ({
  useRelationValidation: () => ({ validation: null, validate: vi.fn(), validating: false }),
}))

vi.mock('@/features/graph/hooks/useGraphRelationActions', () => ({
  useGraphRelationActions: () => ({
    invalidateGraph: vi.fn(),
    createRelationMut: { mutate: vi.fn(), isPending: false },
    updateRelationMut: { mutate: vi.fn(), isPending: false },
    deleteRelationMut: { mutate: vi.fn(), isPending: false },
  }),
}))

function graphTestWrapper({ children }: { children: ReactNode }) {
  const QueryWrapper = createHookWrapper()
  return (
    <MemoryRouter initialEntries={['/graph?root=5']}>
      <QueryWrapper>{children}</QueryWrapper>
    </MemoryRouter>
  )
}

describe('useGraphPageState', () => {
  it('reads root from search params and defaults depth to 3', () => {
    const { result } = renderHook(() => useGraphPageState(), { wrapper: graphTestWrapper })
    expect(result.current.rootId).toBe('5')
    expect(result.current.id).toBe(5)
    expect(result.current.depth).toBe(3)
    expect(result.current.relationFilter).toBe('')
  })
})

describe('useGraphPage', () => {
  it('exposes graph data with create/edit drafts closed', () => {
    const { result } = renderHook(() => {
      const state = useGraphPageState()
      return useGraphPage(state)
    }, { wrapper: graphTestWrapper })

    expect(result.current.createDraft).toBeNull()
    expect(result.current.editDraft).toBeNull()
    expect(result.current.autodiscoverOpen).toBe(false)
    expect(result.current.graph?.nodes).toHaveLength(1)
    expect(result.current.canEdit).toBe(true)
  })
})
