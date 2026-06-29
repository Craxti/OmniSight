import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Button } from '@/shared/components/Button'

describe('Button', () => {
  it('renders primary variant with semantic class', () => {
    render(<Button>Save</Button>)
    const btn = screen.getByRole('button', { name: 'Save' })
    expect(btn).toHaveClass('btn', 'btn-primary')
  })

  it('renders danger variant', () => {
    render(<Button variant="danger">Delete</Button>)
    expect(screen.getByRole('button', { name: 'Delete' })).toHaveClass('btn-danger')
  })

  it('forwards native button props', () => {
    render(<Button disabled data-testid="btn">X</Button>)
    expect(screen.getByTestId('btn')).toBeDisabled()
  })
})
