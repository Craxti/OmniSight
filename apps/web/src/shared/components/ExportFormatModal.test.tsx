import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ExportFormatModal } from '@/shared/components/ExportFormatModal'
import { renderWithProviders } from '@/test/renderWithProviders'

describe('ExportFormatModal', () => {
  it('renders format selector when open', () => {
    renderWithProviders(
      <ExportFormatModal
        open
        title="Export data"
        formatLabel="Format"
        cancelLabel="Cancel"
        submitLabel="Export"
        onClose={vi.fn()}
        onExport={vi.fn()}
      />,
    )
    expect(screen.getByText('Export data')).toBeInTheDocument()
    expect(screen.getByText('Format')).toBeInTheDocument()
    expect(screen.getByTestId('export-format-select')).toHaveValue('xlsx')
  })

  it('calls onExport with selected format', () => {
    const onExport = vi.fn()
    renderWithProviders(
      <ExportFormatModal
        open
        title="Export data"
        formatLabel="Format"
        cancelLabel="Cancel"
        submitLabel="Export"
        onClose={vi.fn()}
        onExport={onExport}
      />,
    )
    fireEvent.change(screen.getByTestId('export-format-select'), { target: { value: 'csv' } })
    fireEvent.click(screen.getByTestId('export-format-submit'))
    expect(onExport).toHaveBeenCalledWith('csv')
  })

  it('does not render when closed', () => {
    renderWithProviders(
      <ExportFormatModal
        open={false}
        title="Export data"
        formatLabel="Format"
        cancelLabel="Cancel"
        submitLabel="Export"
        onClose={vi.fn()}
        onExport={vi.fn()}
      />,
    )
    expect(screen.queryByText('Export data')).not.toBeInTheDocument()
  })
})
