import type { CiStatus } from '@/shared/constants'
import { STATUS_COLORS } from '@/lib/utils'
import { ChartEmptyState } from '@/shared/components/ChartEmptyState'
import { DistributionBar } from '@/shared/components/DistributionLegend'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
type StatusLabels = Record<CiStatus, string>

interface StatusDistributionChartProps {
  byStatus: Record<string, number>
  labels: StatusLabels
  emptyLabel: string
}

export function StatusDistributionChart({ byStatus, labels, emptyLabel }: StatusDistributionChartProps) {
  const { ciStatuses } = useDomainConstants()
  const items = ciStatuses.map((status) => ({
    key: status,
    status,
    label: labels[status as CiStatus] ?? status,
    value: byStatus[status] ?? 0,
    color: STATUS_COLORS[status] ?? '#64748b',
  }))
  const total = items.reduce((sum, item) => sum + item.value, 0)

  if (total === 0) {
    return <ChartEmptyState label={emptyLabel} />
  }

  return (
    <div className="flex h-60 flex-col justify-center gap-6 py-2">
      <DistributionBar items={items} total={total} />

      <div className="space-y-3.5">
        {items.map((item) => {
          const pct = Math.round((item.value / total) * 100)
          return (
            <div key={item.status} className="group">
              <div className="mb-1.5 flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2.5">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full ring-2 ring-white/10"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="truncate text-sm text-[var(--text-primary)]">{item.label}</span>
                </div>
                <div className="flex shrink-0 items-baseline gap-2.5">
                  <span className="text-sm font-semibold tabular-nums text-[var(--text-primary)]">{item.value}</span>
                  <span className="w-9 text-right text-xs tabular-nums text-[var(--text-muted)]">{pct}%</span>
                </div>
              </div>
              <div className="h-1 overflow-hidden rounded-full bg-[var(--bg-muted)]">
                <div
                  className="h-full rounded-full transition-[width] duration-500 group-hover:opacity-90"
                  style={{ width: `${pct}%`, backgroundColor: item.color }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
