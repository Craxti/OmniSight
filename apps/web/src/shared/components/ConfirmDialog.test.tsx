import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ConfirmDialog } from '@/shared/components/ConfirmDialog'
import { renderWithProviders } from '@/test/renderWithProviders'

describe('ConfirmDialog', () => {
  it('renders message and calls onConfirm', () => {
    const onConfirm = vi.fn()
    const onClose = vi.fn()
    renderWithProviders(
      <ConfirmDialog
        open
        title="Delete item"
        message="Are you sure?"
        confirmLabel="Delete"
        onClose={onClose}
        onConfirm={onConfirm}
        confirmTestId="confirm-delete"
      />,
    )
    expect(screen.getByText('Are you sure?')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('confirm-delete'))
    expect(onConfirm).toHaveBeenCalled()
  })

  it('does not render when closed', () => {
    renderWithProviders(
      <ConfirmDialog
        open={false}
        title="Delete item"
        message="Hidden"
        confirmLabel="Delete"
        onClose={vi.fn()}
        onConfirm={vi.fn()}
      />,
    )
    expect(screen.queryByText('Hidden')).not.toBeInTheDocument()
  })
})
