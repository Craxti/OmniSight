import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { RelationCreateModal } from '@/features/relations/components/RelationCreateModal'
import { messages } from '@/i18n/messages'
import { renderWithProviders } from '@/test/renderWithProviders'

const t = messages.ru

vi.mock('@/shared/hooks/useDomainConstants', () => ({
  useDomainConstants: () => ({
    relationTypes: ['depends_on', 'hosted_on'],
    relationStatuses: ['active'],
  }),
}))

describe('RelationCreateModal', () => {
  const cis = [
    { id: 1, name: 'srv-a' },
    { id: 2, name: 'srv-b' },
  ]

  it('renders relation form when open', () => {
    renderWithProviders(
      <RelationCreateModal open cis={cis} pending={false} onClose={vi.fn()} onSubmit={vi.fn()} />,
    )
    expect(screen.getByText(t.relations.newRelation)).toBeInTheDocument()
    expect(document.getElementById('rel-source')).toBeInTheDocument()
    expect(document.getElementById('rel-target')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    renderWithProviders(
      <RelationCreateModal open={false} cis={cis} pending={false} onClose={vi.fn()} onSubmit={vi.fn()} />,
    )
    expect(screen.queryByText(t.relations.newRelation)).not.toBeInTheDocument()
  })

  it('calls onClose from cancel action', () => {
    const onClose = vi.fn()
    renderWithProviders(
      <RelationCreateModal open cis={cis} pending={false} onClose={onClose} onSubmit={vi.fn()} />,
    )
    fireEvent.click(screen.getByRole('button', { name: t.common.cancel }))
    expect(onClose).toHaveBeenCalled()
  })
})
