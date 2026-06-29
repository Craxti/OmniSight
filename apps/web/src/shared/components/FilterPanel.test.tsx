import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import {
  CompactFilterPanel,
  countNonEmptyFilters,
  FilterAdvancedToggle,
  FilterClearButton,
  FilterPanel,
  FilterSearchInput,
  FilterTextInput,
  FilterToolbarSearch,
  hasAnyFilter,
} from '@/shared/components/FilterPanel'

describe('FilterPanel', () => {
  it('renders children inside card grid', () => {
    render(
      <FilterPanel testId="test-filters">
        <span>child</span>
      </FilterPanel>,
    )
    expect(screen.getByTestId('test-filters')).toBeInTheDocument()
    expect(screen.getByText('child')).toBeInTheDocument()
  })

  it('CompactFilterPanel renders compact card', () => {
    render(
      <CompactFilterPanel testId="compact-filters">
        <span>compact</span>
      </CompactFilterPanel>,
    )
    expect(screen.getByTestId('compact-filters')).toBeInTheDocument()
    expect(screen.getByText('compact')).toBeInTheDocument()
  })

  it('FilterSearchInput calls onChange', () => {
    const onChange = vi.fn()
    render(<FilterSearchInput value="" placeholder="Search" testId="search" onChange={onChange} />)
    fireEvent.change(screen.getByTestId('search'), { target: { value: 'abc' } })
    expect(onChange).toHaveBeenCalledWith('abc')
  })

  it('FilterToolbarSearch calls onChange', () => {
    const onChange = vi.fn()
    render(<FilterToolbarSearch value="" placeholder="Search" testId="toolbar-search" onChange={onChange} />)
    fireEvent.change(screen.getByTestId('toolbar-search'), { target: { value: 'abc' } })
    expect(onChange).toHaveBeenCalledWith('abc')
  })

  it('FilterTextInput calls onChange', () => {
    const onChange = vi.fn()
    render(<FilterTextInput value="" placeholder="Owner" testId="owner" onChange={onChange} />)
    fireEvent.change(screen.getByTestId('owner'), { target: { value: 'x' } })
    expect(onChange).toHaveBeenCalledWith('x')
  })

  it('FilterTextInput renders optional label', () => {
    render(<FilterTextInput value="" label="Owner" placeholder="Owner name" testId="owner" onChange={vi.fn()} />)
    expect(screen.getByText('Owner')).toBeInTheDocument()
  })

  it('FilterAdvancedToggle toggles and shows active count badge', () => {
    const onToggle = vi.fn()
    const { rerender } = render(
      <FilterAdvancedToggle
        expanded={false}
        activeCount={2}
        moreLabel="More"
        hideLabel="Hide"
        onToggle={onToggle}
      />,
    )
    expect(screen.getByText('2')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /more/i }))
    expect(onToggle).toHaveBeenCalled()

    rerender(
      <FilterAdvancedToggle
        expanded
        activeCount={2}
        moreLabel="More"
        hideLabel="Hide"
        onToggle={onToggle}
      />,
    )
    expect(screen.getByText('Hide')).toBeInTheDocument()
    expect(screen.queryByText('2')).not.toBeInTheDocument()
  })

  it('FilterClearButton hides when not visible', () => {
    const { rerender } = render(<FilterClearButton visible={false} label="Clear" onClick={vi.fn()} />)
    expect(screen.queryByRole('button', { name: 'Clear' })).not.toBeInTheDocument()

    const onClick = vi.fn()
    rerender(<FilterClearButton visible label="Clear" onClick={onClick} />)
    fireEvent.click(screen.getByRole('button', { name: 'Clear' }))
    expect(onClick).toHaveBeenCalled()
  })

  it('countNonEmptyFilters and hasAnyFilter', () => {
    const filters = { q: 'x', status: '', owner: '  ' }
    expect(countNonEmptyFilters(filters, ['q', 'status', 'owner'])).toBe(1)
    expect(hasAnyFilter(filters)).toBe(true)
    expect(hasAnyFilter({ q: '', status: '' })).toBe(false)
  })
})
