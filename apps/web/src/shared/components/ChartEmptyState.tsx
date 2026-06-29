type Props = {
  label: string
}

export function ChartEmptyState({ label }: Props) {
  return (
    <div className="flex h-60 items-center justify-center text-sm text-[var(--text-muted)]">
      {label}
    </div>
  )
}
