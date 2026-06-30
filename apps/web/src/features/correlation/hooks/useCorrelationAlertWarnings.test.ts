import { describe, expect, it } from 'vitest'
import { renderHook } from '@testing-library/react'
import { messages } from '@/i18n/messages'
import { useCorrelationAlertWarnings } from '@/features/correlation/hooks/useCorrelationAlertWarnings'

describe('useCorrelationAlertWarnings', () => {
  it('flags empty alert rows', () => {
    const { result } = renderHook(() =>
      useCorrelationAlertWarnings([{ hostname: 'app-01' }, {}], ['hostname', 'ip'], messages.en),
    )

    expect(result.current.emptyRowNumbers).toEqual([2])
    expect(result.current.hasWarnings).toBe(true)
  })

  it('has no warnings for rows with identifiers only', () => {
    const { result } = renderHook(() =>
      useCorrelationAlertWarnings([{ hostname: 'app-01' }], ['hostname', 'ip'], messages.en),
    )

    expect(result.current.emptyRowNumbers).toEqual([])
  })
})
