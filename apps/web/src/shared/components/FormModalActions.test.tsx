import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FormModalActions } from '@/shared/components/FormModalActions'

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({ t: { common: { cancel: 'Cancel' } } }),
}))

describe('FormModalActions', () => {
  it('renders split layout with footer note', () => {
    render(
      <FormModalActions
        layout="split"
        footerNote="Blocked reason"
        onCancel={vi.fn()}
        submitLabel="Save"
        submitDisabled
      />,
    )
    expect(screen.getByText('Blocked reason')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled()
  })
})
