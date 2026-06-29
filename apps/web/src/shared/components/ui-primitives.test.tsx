import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Modal } from '@/shared/components/ui-primitives'
import { renderWithProviders } from '@/test/renderWithProviders'

describe('Modal', () => {
  it('renders title and content when open', () => {
    renderWithProviders(
      <Modal open onClose={vi.fn()} title="Create CI">
        <p>Form body</p>
      </Modal>,
    )
    expect(screen.getByText('Create CI')).toBeInTheDocument()
    expect(screen.getByText('Form body')).toBeInTheDocument()
  })

  it('calls onClose when dialog close button is clicked', () => {
    const onClose = vi.fn()
    renderWithProviders(
      <Modal open onClose={onClose} title="Create CI">
        <p>Form body</p>
      </Modal>,
    )
    fireEvent.click(screen.getByRole('button', { name: 'Закрыть' }))
    expect(onClose).toHaveBeenCalled()
  })

  it('does not render content when closed', () => {
    renderWithProviders(
      <Modal open={false} onClose={vi.fn()} title="Hidden">
        <p>Hidden body</p>
      </Modal>,
    )
    expect(screen.queryByText('Hidden body')).not.toBeInTheDocument()
  })
})
