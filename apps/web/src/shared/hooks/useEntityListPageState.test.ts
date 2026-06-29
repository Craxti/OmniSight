import { act, renderHook } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { useEntityListPageState } from '@/shared/hooks/useEntityListPageState'

describe('useEntityListPageState', () => {
  it('initializes and updates shared list-page state', () => {
    const { result } = renderHook(() =>
      useEntityListPageState({ filters: { q: '' }, form: { name: '' } }),
    )

    expect(result.current.filters).toEqual({ q: '' })
    expect(result.current.showForm).toBe(false)
    expect(result.current.importReport).toBeNull()

    act(() => result.current.setFilters({ q: 'db' }))
    act(() => result.current.setShowForm(true))
    act(() => result.current.setImportReport({ created: 1, updated: 0, skipped: 0, errors: [] }))

    expect(result.current.filters).toEqual({ q: 'db' })
    expect(result.current.showForm).toBe(true)
    expect(result.current.importReport?.created).toBe(1)
  })
})
