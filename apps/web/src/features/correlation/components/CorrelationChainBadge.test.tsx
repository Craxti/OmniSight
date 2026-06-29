import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { messages } from '@/i18n/messages'
import { CorrelationChainBadge } from '@/features/correlation/components/CorrelationChainBadge'

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({ t: messages.en }),
}))

describe('CorrelationChainBadge', () => {
  it('shows single-incident label when chain is related', () => {
    render(<CorrelationChainBadge chainRelated />)
    const el = screen.getByTestId('correlation-chain-related')
    expect(el).toHaveAttribute('data-chain-related', 'true')
    expect(el).toHaveTextContent(messages.en.correlation.incidentSingle)
  })

  it('shows separate-incidents label when chain is not related', () => {
    render(<CorrelationChainBadge chainRelated={false} />)
    const el = screen.getByTestId('correlation-chain-related')
    expect(el).toHaveAttribute('data-chain-related', 'false')
    expect(el).toHaveTextContent(messages.en.correlation.incidentSeparate)
  })
})
