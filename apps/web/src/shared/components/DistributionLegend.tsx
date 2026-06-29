type DistributionLegendItem = {
  key: string
  label: string
  value: number
  color: string
  icon?: React.ReactNode
}

type DistributionLegendProps = {
  items: DistributionLegendItem[]
  total: number
  activeKey?: string
  onHover?: (key: string | undefined) => void
  compact?: boolean
  className?: string
}

export function DistributionLegend({
  items,
  total,
  activeKey,
  onHover,
  compact = false,
  className = '',
}: DistributionLegendProps) {
  if (total === 0) return null

  return (
    <div
      className={`flex min-h-0 flex-col justify-start gap-1 overflow-y-auto ${compact ? 'h-full max-h-full shrink-0 min-w-[8.5rem] sm:min-w-[10rem]' : 'max-h-full flex-1'} ${className}`}
    >
      {items.map((item) => {
        const pct = Math.round((item.value / total) * 100)
        const isActive = activeKey === item.key
        return (
          <button
            key={item.key}
            type="button"
            className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left transition-colors ${
              isActive ? 'bg-[var(--bg-hover)]' : 'hover:bg-[var(--bg-hover)]'
            }`}
            onMouseEnter={() => onHover?.(item.key)}
            onMouseLeave={() => onHover?.(undefined)}
          >
            {item.icon ?? (
              <span
                className="h-2.5 w-2.5 shrink-0 rounded-full ring-2 ring-white/10"
                style={{ backgroundColor: item.color }}
              />
            )}
            <span className="min-w-0 flex-1">
              <span className="block truncate text-xs text-[var(--text-primary)]">{item.label}</span>
              <span className="text-caption tabular-nums text-[var(--text-muted)]">
                {item.value} · {pct}%
              </span>
            </span>
          </button>
        )
      })}
    </div>
  )
}

type DistributionBarProps = {
  items: Array<{ key: string; value: number; color: string; label: string }>
  total: number
}

export function DistributionBar({ items, total }: DistributionBarProps) {
  if (total === 0) return null

  return (
    <div className="flex h-2.5 overflow-hidden rounded-full bg-[var(--bg-muted)]">
      {items
        .filter((item) => item.value > 0)
        .map((item) => (
          <div
            key={item.key}
            className="h-full transition-[width] duration-500"
            style={{ width: `${(item.value / total) * 100}%`, backgroundColor: item.color }}
            title={`${item.label}: ${item.value}`}
          />
        ))}
    </div>
  )
}
