import { useState } from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Sector, Tooltip } from 'recharts'
import type { PieSectorShapeProps } from 'recharts'
import { getCiTypeVisual } from '@/lib/graphVisuals'
import { ChartEmptyState } from '@/shared/components/ChartEmptyState'
import { DistributionLegend } from '@/shared/components/DistributionLegend'

interface TypeDistributionChartProps {
  byType: Record<string, number>
  emptyLabel: string
}

type TypeItem = {
  name: string
  value: number
  color: string
}

function renderSlice(props: PieSectorShapeProps, activeIndex: number | undefined) {
  const { cx = 0, cy = 0, innerRadius = 0, outerRadius = 0, startAngle = 0, endAngle = 0, fill, isActive, index } = props
  const highlighted = isActive || activeIndex === index
  return (
    <Sector
      cx={cx}
      cy={cy}
      innerRadius={highlighted ? innerRadius - 1 : innerRadius}
      outerRadius={highlighted ? outerRadius + 5 : outerRadius}
      startAngle={startAngle}
      endAngle={endAngle}
      fill={fill}
      cornerRadius={highlighted ? 5 : 3}
    />
  )
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: TypeItem }> }) {
  if (!active || !payload?.length) return null
  const item = payload[0].payload
  return (
    <div className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] px-3 py-2 shadow-lg">
      <div className="text-sm font-medium text-[var(--text-primary)]">{item.name}</div>
      <div className="mt-0.5 text-xs text-[var(--text-muted)]">{item.value} CI</div>
    </div>
  )
}

export function TypeDistributionChart({ byType, emptyLabel }: TypeDistributionChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | undefined>(undefined)

  const items: TypeItem[] = Object.entries(byType)
    .map(([name, value]) => ({
      name,
      value,
      color: getCiTypeVisual(name).accent,
    }))
    .filter((item) => item.value > 0)
    .sort((a, b) => b.value - a.value || a.name.localeCompare(b.name))

  const total = items.reduce((sum, item) => sum + item.value, 0)

  if (total === 0) {
    return <ChartEmptyState label={emptyLabel} />
  }

  const activeKey = activeIndex !== undefined ? items[activeIndex]?.name : undefined

  return (
    <div className="flex h-60 items-stretch gap-3 sm:gap-5">
      <div className="relative h-full min-w-0 flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={items}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius="56%"
              outerRadius="88%"
              paddingAngle={2}
              stroke="var(--bg-card)"
              strokeWidth={3}
              animationBegin={0}
              animationDuration={550}
              animationEasing="ease-out"
              shape={(props) => renderSlice(props, activeIndex)}
              onMouseEnter={(_, index) => setActiveIndex(index)}
              onMouseLeave={() => setActiveIndex(undefined)}
            >
              {items.map((item) => (
                <Cell key={item.name} fill={item.color} className="outline-none" />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold tabular-nums leading-none text-[var(--text-primary)]">{total}</span>
          <span className="text-caption mt-1 font-medium uppercase tracking-wider text-[var(--text-muted)]">CI</span>
        </div>
      </div>

      <DistributionLegend
        items={items.map((item) => {
          const Icon = getCiTypeVisual(item.name).icon
          return {
            key: item.name,
            label: item.name,
            value: item.value,
            color: item.color,
            icon: (
              <span
                className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md"
                style={{ backgroundColor: getCiTypeVisual(item.name).iconBg, color: item.color }}
              >
                <Icon className="h-3.5 w-3.5" />
              </span>
            ),
          }
        })}
        total={total}
        activeKey={activeKey}
        onHover={(key) => {
          if (!key) {
            setActiveIndex(undefined)
            return
          }
          const idx = items.findIndex((item) => item.name === key)
          setActiveIndex(idx >= 0 ? idx : undefined)
        }}
        compact
      />
    </div>
  )
}
