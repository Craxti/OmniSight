import { waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { defaultCiForm, validateCiForm } from '@/features/inventory/inventoryForm'
import { messages } from '@/i18n/messages'
import { renderAppHook } from '@/test/renderHookWithProviders'
import { useInventoryPage } from '@/features/inventory/hooks/useInventoryPage'

vi.mock('@/context/useAuth', () => ({
  useAuth: () => ({ canEdit: true }),
}))

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({ t: messages.en, success: vi.fn() }),
}))

vi.mock('@/context/useToast', () => ({
  useToast: () => ({ success: vi.fn() }),
}))

vi.mock('@/shared/hooks/useCiTypes', () => ({
  useCiTypes: () => ({ data: [] }),
}))

vi.mock('@/shared/api', () => ({
  ciApi: {
    listPage: vi.fn().mockResolvedValue({
      items: [{ id: 1, name: 'srv-1' }],
      pagination: { page: 1, page_size: 50, total_items: 1, total_pages: 1 },
    }),
    recycleBin: vi.fn().mockResolvedValue([]),
  },
}))

vi.mock('@/features/inventory/hooks/useCiMutations', () => ({
  useCiMutations: () => ({
    createMut: { mutate: vi.fn(), isPending: false },
    deleteMut: { mutate: vi.fn() },
    restoreMut: { mutate: vi.fn() },
    purgeMut: { mutate: vi.fn() },
    bulkMut: { mutate: vi.fn() },
    bulkDeleteMut: { mutate: vi.fn(), isPending: false },
  }),
}))

describe('useInventoryPage', () => {
  it('loads active inventory items by default', async () => {
    const { result, rerender } = renderAppHook(() => useInventoryPage())
    await waitFor(() => expect(result.current.items).toHaveLength(1))
    expect(result.current.items[0]?.name).toBe('srv-1')
    expect(result.current.view).toBe('active')
    rerender()
  })
})

describe('validateCiForm', () => {
  it('requires owner and environment', () => {
    const err = validateCiForm({ ...defaultCiForm, owner: '' }, messages.en)
    expect(err).toBeTruthy()
  })
})
