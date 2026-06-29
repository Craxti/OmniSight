import type { LucideIcon } from 'lucide-react'

export type TabBarItem<T extends string> = {
  id: T
  label: string
  icon?: LucideIcon
  show?: boolean
}

type TabBarProps<T extends string> = {
  items: TabBarItem<T>[]
  active: T
  onChange: (id: T) => void
  ariaLabel: string
  testId?: string
}

export function TabBar<T extends string>({
  items,
  active,
  onChange,
  ariaLabel,
  testId,
}: TabBarProps<T>) {
  const visible = items.filter((item) => item.show !== false)

  return (
    <div className="settings-tabs" role="tablist" aria-label={ariaLabel} data-testid={testId}>
      {visible.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          type="button"
          role="tab"
          aria-selected={active === id}
          data-active={active === id}
          data-testid={testId ? `${testId}-${id}` : undefined}
          onClick={() => onChange(id)}
        >
          {Icon ? <Icon className="h-4 w-4 opacity-70" aria-hidden /> : null}
          {label}
        </button>
      ))}
    </div>
  )
}
