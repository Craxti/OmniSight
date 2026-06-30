import { act, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { messages } from '@/i18n/messages'
import { renderAppHook } from '@/test/renderHookWithProviders'
import { cleanedAlerts, useCorrelationPage } from '@/features/correlation/hooks/useCorrelationPage'

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({ t: messages.en }),
}))

vi.mock('@/context/useToast', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}))

const ingestMock = vi.fn()

vi.mock('@/shared/api', () => ({
  correlationApi: {
    ingest: (...args: unknown[]) => ingestMock(...args),
  },
}))

describe('cleanedAlerts', () => {
  it('removes empty alert identifier fields', () => {
    expect(cleanedAlerts([{ hostname: 'pay-srv', ip: '', serviceCode: 'PAY' }])).toEqual([
      { hostname: 'pay-srv', serviceCode: 'PAY' },
    ])
  })
})

describe('useCorrelationPage', () => {
  it('starts with one empty alert row and no ingest result', () => {
    const { result } = renderAppHook(() => useCorrelationPage())
    expect(result.current.alerts).toHaveLength(1)
    expect(result.current.ingestResult).toBeNull()
  })

  it('stores ingest response after successful mutation', async () => {
    ingestMock.mockResolvedValueOnce({
      schema_version: 'rsm-correlation-v1',
      resolve: { resolved: [{ resolved: true, ambiguous: false, alert: {}, resource: { id: 1 } }], unresolved: [] },
      correlation: { chain_related: true, resource_ids: [1] },
    })

    const { result } = renderAppHook(() => useCorrelationPage())

    act(() => {
      result.current.setAlerts([{ hostname: 'app-01' }])
    })

    await act(async () => {
      result.current.ingestMut.mutate(undefined)
    })

    await waitFor(() => expect(result.current.ingestResult).not.toBeNull())

    expect(result.current.ingestResult?.correlation?.chain_related).toBe(true)
    expect(ingestMock).toHaveBeenCalledWith(cleanedAlerts([{ hostname: 'app-01' }]), 'ui')
  })
})
