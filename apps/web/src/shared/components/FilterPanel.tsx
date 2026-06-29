import { ChevronDown, SlidersHorizontal } from 'lucide-react'
import { useState, type ReactNode, type SelectHTMLAttributes } from 'react'
import { Button } from '@/shared/components/Button'
import { cn } from '@/lib/utils'

type FilterPanelProps = {
  children: ReactNode
  testId?: string
}

/** Full grid layout — used on audit and similar pages */
export function FilterPanel({ children, testId }: FilterPanelProps) {
  return (
    <div className="card grid grid-cols-1 gap-3 p-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4" data-testid={testId}>
      {children}
    </div>
  )
}

/** Compact card wrapper for toolbar-style filters */
export function CompactFilterPanel({ children, testId }: FilterPanelProps) {
  return (
    <div className="card p-3" data-testid={testId}>
      {children}
    </div>
  )
}

export function FilterToolbar({ children }: { children: ReactNode }) {
  return <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">{children}</div>
}

type FilterSearchInputProps = {
  value: string
  placeholder: string
  testId?: string
  onChange: (value: string) => void
}

export function FilterSearchInput({ value, placeholder, testId, onChange }: FilterSearchInputProps) {
  return (
    <input
      className="input col-span-full"
      placeholder={placeholder}
      aria-label={placeholder}
      data-testid={testId}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

export function FilterToolbarSearch({ value, placeholder, testId, onChange }: FilterSearchInputProps) {
  return (
    <input
      className="input min-w-0 flex-1 sm:min-w-[12rem]"
      placeholder={placeholder}
      aria-label={placeholder}
      data-testid={testId}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

type FilterTextInputProps = {
  value: string
  placeholder: string
  label?: string
  testId?: string
  onChange: (value: string) => void
}

export function FilterTextInput({ value, placeholder, label, testId, onChange }: FilterTextInputProps) {
  const inputId = testId ? `${testId}-input` : undefined
  return (
    <div className="space-y-1">
      {label ? (
        <label htmlFor={inputId} className="label">
          {label}
        </label>
      ) : null}
      <input
        id={inputId}
        className="input"
        placeholder={placeholder}
        aria-label={label ?? placeholder}
        data-testid={testId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

type FilterSelectProps = SelectHTMLAttributes<HTMLSelectElement>

export function FilterSelect({ className, ...props }: FilterSelectProps) {
  return <select className={cn('input w-full sm:w-auto sm:min-w-[9rem]', className)} {...props} />
}

type FilterAdvancedToggleProps = {
  expanded: boolean
  activeCount: number
  moreLabel: string
  hideLabel: string
  onToggle: () => void
}

export function FilterAdvancedToggle({ expanded, activeCount, moreLabel, hideLabel, onToggle }: FilterAdvancedToggleProps) {
  return (
    <Button
      variant="ghost"
      className="shrink-0"
      aria-expanded={expanded}
      onClick={onToggle}
    >
      <SlidersHorizontal className="size-3.5" aria-hidden />
      {expanded ? hideLabel : moreLabel}
      {!expanded && activeCount > 0 && (
        <span className="badge badge-indigo min-w-[1.25rem] justify-center px-1.5">{activeCount}</span>
      )}
      <ChevronDown className={cn('size-3.5 transition-transform', expanded && 'rotate-180')} aria-hidden />
    </Button>
  )
}

type FilterClearButtonProps = {
  visible: boolean
  label: string
  onClick: () => void
}

export function FilterClearButton({ visible, label, onClick }: FilterClearButtonProps) {
  if (!visible) return null
  return (
    <Button variant="ghost" className="shrink-0" onClick={onClick}>
      {label}
    </Button>
  )
}

export function FilterAdvancedGrid({ open, children }: { open: boolean; children: ReactNode }) {
  if (!open) return null
  return (
    <div className="mt-3 grid grid-cols-1 gap-2 border-t border-[var(--border-subtle)] pt-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {children}
    </div>
  )
}

export function countNonEmptyFilters(filters: Record<string, string>, keys: readonly string[]): number {
  return keys.filter((key) => filters[key]?.trim()).length
}

export function hasAnyFilter(filters: Record<string, string>): boolean {
  return Object.values(filters).some((value) => value.trim())
}

export function useFilterAdvancedSection(advancedKeys: readonly string[], filters: Record<string, string>) {
  const advancedActiveCount = countNonEmptyFilters(filters, advancedKeys)
  const [expanded, setExpanded] = useState(() => advancedActiveCount > 0)
  return {
    expanded,
    advancedActiveCount,
    toggle: () => setExpanded((value) => !value),
  }
}
