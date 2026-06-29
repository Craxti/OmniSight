import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { FieldLabel } from '@/shared/components/Label'

describe('FieldLabel', () => {
  it('associates label with control', () => {
    render(
      <>
        <FieldLabel htmlFor="owner">Owner</FieldLabel>
        <input id="owner" aria-label="owner field" />
      </>,
    )
    expect(screen.getByText('Owner')).toBeInTheDocument()
  })

  it('shows required marker', () => {
    render(<FieldLabel required>Name</FieldLabel>)
    expect(screen.getByText('*')).toBeInTheDocument()
  })
})
