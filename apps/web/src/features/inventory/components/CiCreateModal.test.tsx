import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { CiCreateModal } from '@/features/inventory/components/CiCreateModal'
import { messages } from '@/i18n/messages'
import { renderWithProviders } from '@/test/renderWithProviders'

const t = messages.ru

vi.mock('@/shared/hooks/useDomainConstants', () => ({
  useDomainConstants: () => ({
    ciStatuses: ['active'],
    criticalityLevels: ['medium'],
    externalIdFields: ['hostname'],
    environments: ['production', 'test'],
  }),
}))

vi.mock('@/features/inventory/hooks/useDuplicateWarnings', () => ({
  useDuplicateWarnings: () => ({
    dupWarnings: {},
    ipFormatError: null,
    getExternalHint: () => undefined,
  }),
}))

describe('CiCreateModal', () => {
  it('renders create form when open', () => {
    renderWithProviders(
      <CiCreateModal
        open
        types={[{ id: 1, name: 'Server' }]}
        isPending={false}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />,
    )
    expect(screen.getByText(t.inventory.newCi)).toBeInTheDocument()
    expect(document.getElementById('ci-name')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    renderWithProviders(
      <CiCreateModal
        open={false}
        types={[]}
        isPending={false}
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />,
    )
    expect(screen.queryByText(t.inventory.newCi)).not.toBeInTheDocument()
  })

  it('calls onClose from cancel action', () => {
    const onClose = vi.fn()
    renderWithProviders(
      <CiCreateModal
        open
        types={[{ id: 1, name: 'Server' }]}
        isPending={false}
        onClose={onClose}
        onSubmit={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByRole('button', { name: t.common.cancel }))
    expect(onClose).toHaveBeenCalled()
  })
})
