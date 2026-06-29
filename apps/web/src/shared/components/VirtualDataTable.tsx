import { useVirtualizer } from '@tanstack/react-virtual'

import { useCallback, useLayoutEffect, useMemo, useRef, type CSSProperties, type ReactNode } from 'react'

import { EmptyState, Skeleton } from '@/components/ui'



export type VirtualColumn<T> = {

  id: string

  header: ReactNode

  width?: string

  className?: string

  headerClassName?: string

  cellClassName?: string

  cell: (row: T, index: number) => ReactNode

  /** Omit from mobile card layout */

  hideMobile?: boolean

}



type VirtualDataTableProps<T> = {

  items: T[]

  columns: VirtualColumn<T>[]

  getRowKey: (row: T) => string | number

  isLoading?: boolean

  loadingRows?: number

  empty?: ReactNode

  rowHeight?: number

  maxHeight?: string

  className?: string

  ariaLabel?: string

  testId?: string

  /** Disable row virtualization for variable-height content (e.g. audit diffs). */

  virtualized?: boolean

}



function TableHeader<T>({
  columns,
  gridTemplateColumns,
}: {
  columns: VirtualColumn<T>[]
  gridTemplateColumns: string
}) {
  return (
    <div
      className="virtual-table-header hidden min-w-full md:grid"
      style={{ gridTemplateColumns }}
      role="row"
    >
      {columns.map((col) => (
        <div key={col.id} className={`virtual-table-th ${col.headerClassName ?? ''}`} role="columnheader">
          {col.header}
        </div>
      ))}
    </div>
  )
}

/** In-flow row that establishes a single table width for header/body column alignment. */
function TableWidthSizer<T>({
  columns,
  gridTemplateColumns,
}: {
  columns: VirtualColumn<T>[]
  gridTemplateColumns: string
}) {
  return (
    <div
      className="virtual-table-row virtual-table-width-sizer grid"
      style={{ gridTemplateColumns }}
      aria-hidden
    >
      {columns.map((col) => (
        <div key={col.id} className="virtual-table-td" />
      ))}
    </div>
  )
}



export function VirtualDataTable<T>({

  items,

  columns,

  getRowKey,

  isLoading = false,

  loadingRows = 5,

  empty,

  rowHeight = 52,

  maxHeight = 'min(70vh, 720px)',

  className = '',

  ariaLabel,

  testId,

  virtualized = true,

}: VirtualDataTableProps<T>) {

  const bodyScrollRef = useRef<HTMLDivElement>(null)

  const headerScrollRef = useRef<HTMLDivElement>(null)

  const syncingScrollRef = useRef(false)



  const gridTemplateColumns = useMemo(

    () => columns.map((c) => c.width ?? '1fr').join(' '),

    [columns],

  )



  const mobileColumns = useMemo(

    () => columns.filter((c) => !c.hideMobile && c.id !== 'actions' && c.id !== 'spacer' && c.id !== 'select'),

    [columns],

  )



  const syncHorizontalScroll = useCallback((source: 'header' | 'body') => {
    const header = headerScrollRef.current
    const body = bodyScrollRef.current
    if (!header || !body || syncingScrollRef.current) return

    syncingScrollRef.current = true
    if (source === 'body') {
      header.scrollLeft = body.scrollLeft
    } else {
      body.scrollLeft = header.scrollLeft
    }
    syncingScrollRef.current = false
  }, [])

  useLayoutEffect(() => {
    syncHorizontalScroll('body')
  }, [items.length, gridTemplateColumns, syncHorizontalScroll])



  const rowVirtualizer = useVirtualizer({

    count: items.length,

    getScrollElement: () => bodyScrollRef.current,

    estimateSize: () => rowHeight,

    overscan: 10,

    enabled: virtualized,

  })



  const renderRow = (

    row: T,

    index: number,

    rowProps?: { className?: string; style?: CSSProperties; dataIndex?: number; measureRef?: (node: Element | null) => void },

  ) => (

    <div

      key={getRowKey(row)}

      data-index={rowProps?.dataIndex}

      ref={rowProps?.measureRef}

      className={`virtual-table-row grid w-full min-w-full ${rowProps?.className ?? ''}`.trim()}

      style={{ gridTemplateColumns, ...rowProps?.style }}

      role="row"

    >

      {columns.map((col) => (

        <div

          key={col.id}

          className={`virtual-table-td ${col.className ?? ''} ${col.cellClassName ?? ''}`.trim()}

          role="cell"

        >

          {col.cell(row, index)}

        </div>

      ))}

    </div>

  )



  if (isLoading) {

    return (

      <div className={`virtual-table-wrap ${className}`} data-testid={testId} style={{ maxHeight }}>

        <TableHeader columns={columns} gridTemplateColumns={gridTemplateColumns} />

        <div className="virtual-table-scroll">
          <div className="virtual-table-body w-max min-w-full">
            <TableWidthSizer columns={columns} gridTemplateColumns={gridTemplateColumns} />
            {[...Array(loadingRows)].map((_, i) => (
              <div key={i} className="virtual-table-row hidden w-full md:grid" style={{ gridTemplateColumns }}>

                {columns.map((col) => (

                  <div key={col.id} className="virtual-table-td">

                    <Skeleton className="h-4 w-full" />

                  </div>

                ))}

              </div>

            ))}

          </div>

        </div>

      </div>

    )

  }



  if (items.length === 0) {

    return (

      <div className={`virtual-table-wrap ${className}`} data-testid={testId}>

        <div className="p-4">{empty ?? <EmptyState title="—" />}</div>

      </div>

    )

  }



  const actionsColumn = columns.find((c) => c.id === 'actions')



  return (

    <div className={`virtual-table-wrap ${className}`} data-testid={testId} style={{ maxHeight }}>

      <div

        ref={headerScrollRef}

        className="virtual-table-header-scroll hidden shrink-0 md:block"

        onScroll={() => syncHorizontalScroll('header')}

      >

        <TableHeader columns={columns} gridTemplateColumns={gridTemplateColumns} />

      </div>

      <div

        ref={bodyScrollRef}

        className="virtual-table-scroll"

        onScroll={() => syncHorizontalScroll('body')}

        role="table"

        aria-label={ariaLabel}

      >

        <div
          className={`virtual-table-body w-max min-w-full ${virtualized ? 'relative hidden md:block' : 'hidden md:block'}`}
          style={virtualized ? { height: rowVirtualizer.getTotalSize() } : undefined}
          role="rowgroup"
        >
          <TableWidthSizer columns={columns} gridTemplateColumns={gridTemplateColumns} />
          {virtualized
            ? rowVirtualizer.getVirtualItems().map((virtualRow) => {
                const row = items[virtualRow.index]
                return renderRow(row, virtualRow.index, {
                  className: 'virtual-table-row-virtual',
                  dataIndex: virtualRow.index,
                  measureRef: rowVirtualizer.measureElement,
                  style: {
                    height: `${virtualRow.size}px`,
                    transform: `translateY(${virtualRow.start}px)`,
                  },
                })
              })
            : items.map((row, index) => renderRow(row, index))}
        </div>

        <div className="virtual-table-mobile md:hidden" role="rowgroup">

          {items.map((row, index) => (

            <div key={getRowKey(row)} className="virtual-table-mobile-card" role="row">

              {mobileColumns.map((col) => (

                <div key={col.id} className="virtual-table-mobile-field">

                  <span className="virtual-table-mobile-label">{col.header}</span>

                  <span className="virtual-table-mobile-value">{col.cell(row, index)}</span>

                </div>

              ))}

              {actionsColumn && (

                <div className="virtual-table-mobile-actions">

                  {actionsColumn.cell(row, index)}

                </div>

              )}

            </div>

          ))}

        </div>

      </div>

    </div>

  )

}

