import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { useApiMutation } from '@/shared/hooks/useApiMutation'

const success = vi.fn()
const error = vi.fn()

vi.mock('../../context/useToast', () => ({
  useToast: () => ({ success, error }),
}))

function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>
}

describe('useApiMutation', () => {
  it('invalidates keys and shows success toast on success', async () => {
    success.mockClear()
    const invalidateSpy = vi.spyOn(QueryClient.prototype, 'invalidateQueries')

    const { result } = renderHook(
      () =>
        useApiMutation({
          mutationFn: async (value: string) => ({ ok: value }),
          invalidateKeys: [['demo']],
          messages: { success: 'Saved', error: 'Failed' },
        }),
      { wrapper },
    )

    result.current.mutate('test')
    await waitFor(() => expect(result.current.isSuccess).toBe(true))

    expect(success).toHaveBeenCalledWith('Saved')
    expect(invalidateSpy).toHaveBeenCalled()
    invalidateSpy.mockRestore()
  })

  it('shows error toast on failure', async () => {
    error.mockClear()

    const { result } = renderHook(
      () =>
        useApiMutation({
          mutationFn: async () => {
            throw new Error('boom')
          },
          messages: { success: 'Saved', error: 'Failed' },
        }),
      { wrapper },
    )

    result.current.mutate(undefined as void)
    await waitFor(() => expect(result.current.isError).toBe(true))

    expect(error).toHaveBeenCalledWith('boom')
  })
})
