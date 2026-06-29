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
    expect(result.current.correlationGraph).toBeNull()
    expect(result.current.ambiguousCount).toBe(0)
  })

  it('derives graph highlights after successful ingest', async () => {
    ingestMock.mockResolvedValueOnce({
      resolve: { resolved: [{ resolved: true, ambiguous: false, alert: {}, resource: { id: 1 } }] },
      correlation: {
        resource_ids: [1, 2],
        potential_root_cause_zone: [{ id: 2, name: 'db' }],
        graph: {
          nodes: [
            { id: 1, name: 'app' },
            { id: 2, name: 'db' },
          ],
          edges: [{ source_ci_id: 2, target_ci_id: 1, relation_type: 'depends_on' }],
        },
        enrichment: [{ id: 1 }],
      },
    })

    const { result } = renderAppHook(() => useCorrelationPage())

    act(() => {
      result.current.setAlerts([{ hostname: 'app-01' }])
    })

    await act(async () => {
      result.current.ingestMut.mutate(undefined)
    })

    await waitFor(() => expect(result.current.ingestResult).not.toBeNull())

    expect(result.current.correlationGraph?.nodes).toHaveLength(2)
    expect(result.current.rootCauseRootId).toBe(2)
    expect(result.current.correlationPathEdgeKeys).toEqual(['2-1'])
    expect(result.current.staleContext).toBe(false)
    expect(ingestMock).toHaveBeenCalledWith(cleanedAlerts([{ hostname: 'app-01' }]), 'ui')
  })
})
