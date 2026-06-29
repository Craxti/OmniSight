import type { ReactNode } from 'react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'

type PaginationBarProps = {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  /** `one` — page starts at 1 (default); `zero` — page starts at 0. */
  pageBase?: 'one' | 'zero'
  summary?: ReactNode
  className?: string
  pageSize?: number
  pageSizeOptions?: readonly number[]
  onPageSizeChange?: (size: number) => void
}

export function PaginationBar({
  page,
  totalPages,
  onPageChange,
  pageBase = 'one',
  summary,
  className = '',
  pageSize,
  pageSizeOptions,
  onPageSizeChange,
}: PaginationBarProps) {
  const { t } = useI18n()
  const displayPage = pageBase === 'zero' ? page + 1 : page
  const atStart = pageBase === 'zero' ? page <= 0 : page <= 1
  const atEnd = pageBase === 'zero' ? page + 1 >= totalPages : page >= totalPages

  const goPrev = () => onPageChange(pageBase === 'zero' ? page - 1 : page - 1)
  const goNext = () => onPageChange(pageBase === 'zero' ? page + 1 : page + 1)

  return (
    <div className={`flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between ${className}`}>
      {summary ? <div className="text-sm text-[var(--text-muted)]">{summary}</div> : <span />}
      <div className="flex flex-wrap items-center justify-end gap-2">
        {pageSize != null && pageSizeOptions && onPageSizeChange ? (
          <label className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
            <span className="hidden sm:inline">{t.common.pageSize}</span>
            <select
              className="input w-auto py-1.5 text-sm"
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              aria-label={t.common.pageSize}
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </label>
        ) : null}
        <Button variant="secondary" className="min-h-11 sm:min-h-0" disabled={atStart} onClick={goPrev} aria-label={t.common.prevPage}>
          ←
        </Button>
        <span className="text-sm text-[var(--text-muted)]">
          {displayPage} / {totalPages}
        </span>
        <Button variant="secondary" className="min-h-11 sm:min-h-0" disabled={atEnd} onClick={goNext} aria-label={t.common.nextPage}>
          →
        </Button>
      </div>
    </div>
  )
}
