import { Skeleton } from '@/components/ui'

type BusyProps = {
  label?: string
}

const busy = (label?: string) =>
  ({
    role: 'status',
    'aria-busy': true,
    'aria-live': 'polite',
    ...(label ? { 'aria-label': label } : {}),
  }) as const

export function StatCardsSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {[...Array(count)].map((_, i) => (
        <Skeleton key={i} className="h-24 w-full rounded-xl" />
      ))}
    </div>
  )
}

export function ChartCardsSkeleton({ count = 2 }: { count?: number }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="card p-5">
          <Skeleton className="mb-4 h-5 w-32" />
          <Skeleton className="h-60 w-full rounded-lg" />
        </div>
      ))}
    </div>
  )
}

/** Same layout as Dashboard / lazy route fallback. */
export function DashboardPageSkeleton({ label }: BusyProps = {}) {
  return (
    <div className="space-y-6 p-1" {...busy(label)}>
      <Skeleton className="h-10 w-64 max-w-full" />
      <StatCardsSkeleton />
      <ChartCardsSkeleton />
    </div>
  )
}

export function CardGridSkeleton({
  count = 6,
  className = 'h-32',
}: {
  count?: number
  className?: string
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {[...Array(count)].map((_, i) => (
        <Skeleton key={i} className={`w-full rounded-xl ${className}`} />
      ))}
    </div>
  )
}

export function DetailPageSkeleton({ label }: BusyProps = {}) {
  return (
    <div className="space-y-6" {...busy(label)}>
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10 shrink-0 rounded-lg" />
        <div className="min-w-0 flex-1 space-y-2">
          <Skeleton className="h-8 w-48 max-w-full" />
          <Skeleton className="h-4 w-72 max-w-full" />
        </div>
      </div>
      <Skeleton className="h-10 w-full max-w-lg rounded-lg" />
      <div className="card space-y-4 p-5">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-10 w-full rounded-md" />
        ))}
      </div>
    </div>
  )
}

/** Correlation ingest / result blocks while waiting for API. */
export function CorrelationResultSkeleton({ label }: BusyProps = {}) {
  return (
    <div className="grid gap-4 lg:grid-cols-2" data-testid="correlation-ingest-loading" {...busy(label)}>
      <Skeleton className="h-40 w-full rounded-xl" />
      <Skeleton className="h-40 w-full rounded-xl" />
      <Skeleton className="h-60 w-full rounded-xl lg:col-span-2" />
    </div>
  )
}

export function GraphCanvasSkeleton({ label }: BusyProps = {}) {
  return (
    <div className="flex h-full flex-col gap-4 p-6" {...busy(label)}>
      <Skeleton className="h-5 w-40" />
      <Skeleton className="min-h-[280px] flex-1 w-full rounded-xl" />
    </div>
  )
}

export function ListRowsSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="space-y-2 rounded-lg border border-[var(--border-subtle)] p-2">
      {[...Array(rows)].map((_, i) => (
        <Skeleton key={i} className="h-9 w-full rounded-md" />
      ))}
    </div>
  )
}

export function TableFiltersSkeleton() {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {[...Array(4)].map((_, i) => (
        <Skeleton key={i} className="h-10 w-full rounded-lg" />
      ))}
    </div>
  )
}

/** Full list page shell: header area + filters + table rows. */
export function TablePageSkeleton({ label }: BusyProps = {}) {
  return (
    <div className="space-y-6" {...busy(label)}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-10 w-28 rounded-lg" />
          <Skeleton className="h-10 w-28 rounded-lg" />
        </div>
      </div>
      <TableFiltersSkeleton />
      <div className="card overflow-hidden p-0">
        <Skeleton className="h-11 w-full rounded-none" />
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="mx-4 my-3 h-9 w-[calc(100%-2rem)] rounded-md" />
        ))}
      </div>
    </div>
  )
}
