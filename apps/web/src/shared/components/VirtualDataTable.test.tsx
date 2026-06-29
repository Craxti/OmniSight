import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'

type Row = { id: number; name: string }

const columns: VirtualColumn<Row>[] = [
  { id: 'name', header: 'Name', cell: (row) => row.name },
  { id: 'actions', header: 'Actions', cell: () => '…' },
]

describe('VirtualDataTable', () => {
  it('shows loading skeleton rows', () => {
    render(
      <VirtualDataTable
        items={[]}
        columns={columns}
        getRowKey={(row) => row.id}
        isLoading
        testId="vtable-loading"
      />,
    )
    expect(screen.getByTestId('vtable-loading')).toBeInTheDocument()
  })

  it('shows empty state when no items', () => {
    render(
      <VirtualDataTable
        items={[]}
        columns={columns}
        getRowKey={(row) => row.id}
        empty={<div>No rows</div>}
        testId="vtable-empty"
      />,
    )
    expect(screen.getByText('No rows')).toBeInTheDocument()
  })

  it('renders rows with table semantics', () => {
    render(
      <VirtualDataTable
        items={[
          { id: 1, name: 'alpha' },
          { id: 2, name: 'beta' },
        ]}
        columns={columns}
        getRowKey={(row) => row.id}
        ariaLabel="Inventory table"
        testId="vtable-data"
        virtualized={false}
      />,
    )
    expect(screen.getByRole('table', { name: 'Inventory table' })).toBeInTheDocument()
    expect(screen.getAllByText('alpha').length).toBeGreaterThan(0)
    expect(screen.getAllByText('beta').length).toBeGreaterThan(0)
  })

  it('renders mobile card layout', () => {
    render(
      <VirtualDataTable
        items={[{ id: 1, name: 'mobile-row' }]}
        columns={columns}
        getRowKey={(row) => row.id}
        virtualized={false}
      />,
    )
    expect(screen.getAllByText('mobile-row').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Name').length).toBeGreaterThan(0)
  })
})
