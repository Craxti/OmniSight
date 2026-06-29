import type { ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { useI18n } from '@/context/useI18n'
import {
  AUDIT_DIFF_INLINE_LIMIT,
  formatAuditValue,
  getChangedAuditKeys,
  isAuditCreation,
  isAuditRemoval,
  truncateAuditValue,
} from '@/features/audit/auditDiff'
import type { ImportReport } from '@/shared/api/types'

export function AppDialog({
  open,
  onOpenChange,
  title,
  children,
  wide = false,
  contentClassName = '',
  testId,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  children: ReactNode
  wide?: boolean
  contentClassName?: string
  testId?: string
}) {
  const { t } = useI18n()
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" />
        <Dialog.Content
          data-testid={testId}
          className={`card fixed left-1/2 top-1/2 z-50 max-h-[90vh] w-[calc(100%-1rem)] max-w-[calc(100vw-1rem)] -translate-x-1/2 -translate-y-1/2 overflow-auto p-4 shadow-2xl focus:outline-none sm:w-[calc(100%-2rem)] sm:p-6 ${wide ? 'sm:max-w-3xl' : 'sm:max-w-lg'} ${contentClassName}`.trim()}
          aria-describedby={undefined}
        >
          <div className="mb-4 flex items-center justify-between gap-3">
            <Dialog.Title className="text-lg font-semibold text-[var(--text-primary)]">{title}</Dialog.Title>
            <Dialog.Close
              type="button"
              className="min-h-11 min-w-11 rounded-lg text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)] focus-brand sm:min-h-0 sm:min-w-0"
              aria-label={t.common.close}
            >
              <X className="h-5 w-5" />
            </Dialog.Close>
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

export function Modal({
  open,
  onClose,
  title,
  children,
  wide,
  testId,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  wide?: boolean
  testId?: string
}) {
  return (
    <AppDialog open={open} onOpenChange={(next) => { if (!next) onClose() }} title={title} wide={wide} testId={testId}>
      {children}
    </AppDialog>
  )
}

export function ImportReportView({ report }: { report: ImportReport }) {
  const { t } = useI18n()
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: t.importReport.created, value: report.created, color: 'text-success' },
          { label: t.importReport.updated, value: report.updated, color: 'text-info' },
          { label: t.importReport.skipped, value: report.skipped, color: 'text-warning' },
          { label: t.importReport.errors, value: report.errors.length, color: 'text-error' },
        ].map(({ label, value, color }) => (
          <div key={label} className="rounded-lg border border-[var(--border)] bg-[var(--surface-muted)] p-3 text-center">
            <div className={`text-2xl font-bold ${color}`}>{value}</div>
            <div className="text-xs text-[var(--text-muted)]">{label}</div>
          </div>
        ))}
      </div>
      {report.errors.length > 0 && (
        <div>
          <div className="label mb-2">{t.importReport.errorsTitle}</div>
          <ul className="max-h-40 space-y-1 overflow-auto rounded-lg alert alert-error p-3 text-xs">
            {report.errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}

export function AuditDiffView({
  oldValue,
  newValue,
  variant = 'detailed',
}: {
  oldValue: Record<string, unknown> | null
  newValue: Record<string, unknown> | null
  variant?: 'inline' | 'detailed'
}) {
  const { t } = useI18n()
  if (!oldValue && !newValue) return null
  const rows = getChangedAuditKeys(oldValue, newValue)
  const removed = isAuditRemoval(oldValue, newValue)
  const created = isAuditCreation(oldValue, newValue)

  if (rows.length === 0) {
    return <span className="text-xs text-[var(--text-muted)]">{t.common.noFieldChanges}</span>
  }

  if (variant === 'inline') {
    const visible = rows.slice(0, AUDIT_DIFF_INLINE_LIMIT)
    const hidden = rows.length - visible.length
    return (
      <div className="space-y-1 text-xs leading-relaxed">
        {visible.map((key) => (
          <AuditDiffLine
            key={key}
            field={key}
            oldValue={oldValue?.[key]}
            newValue={newValue?.[key]}
            compact
            removed={removed}
            created={created}
          />
        ))}
        {hidden > 0 ? (
          <span className="text-[var(--text-muted)]">{t.audit.moreChanges.replace('{n}', String(hidden))}</span>
        ) : null}
      </div>
    )
  }

  return (
    <div className="mt-2 space-y-1">
      {rows.map((key) => (
        <AuditDiffLine
          key={key}
          field={key}
          oldValue={oldValue?.[key]}
          newValue={newValue?.[key]}
          removed={removed}
          created={created}
        />
      ))}
    </div>
  )
}

function AuditDiffLine({
  field,
  oldValue,
  newValue,
  compact = false,
  removed = false,
  created = false,
}: {
  field: string
  oldValue: unknown
  newValue: unknown
  compact?: boolean
  removed?: boolean
  created?: boolean
}) {
  const oldText = truncateAuditValue(formatAuditValue(oldValue))
  const newText = truncateAuditValue(formatAuditValue(newValue))
  const shell = compact
    ? 'min-w-0'
    : 'rounded bg-[var(--surface-muted)] px-2 py-1 text-xs'

  return (
    <div className={shell}>
      <span className="font-medium text-[var(--text-muted)]">{field}: </span>
      {removed ? (
        <span className="text-error/80 line-through">{oldText}</span>
      ) : created ? (
        <span className="text-success">{newText}</span>
      ) : (
        <>
          {oldValue !== undefined && oldValue !== null ? (
            <span className="text-error/80 line-through">{oldText}</span>
          ) : null}
          {oldValue !== undefined && oldValue !== null && newValue !== undefined && newValue !== null ? (
            <span className="mx-1 text-[var(--text-muted)]">→</span>
          ) : null}
          {newValue !== undefined && newValue !== null ? (
            <span className="text-success">{newText}</span>
          ) : null}
        </>
      )}
    </div>
  )
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`skeleton ${className}`} />
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="mb-3 text-4xl opacity-30">◇</div>
      <p className="font-medium text-[var(--text-primary)]">{title}</p>
      {hint && <p className="mt-1 max-w-sm text-sm text-[var(--text-muted)]">{hint}</p>}
    </div>
  )
}

export function PageHeader({
  title,
  subtitle,
  actions,
  className = '',
}: {
  title: string
  subtitle?: string
  actions?: ReactNode
  className?: string
}) {
  return (
    <div className={`page-header ${className}`.trim()}>
      <div className="min-w-0 flex-1">
        <h1 className="page-title text-xl sm:text-2xl">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      {actions && <div className="flex w-full shrink-0 flex-wrap gap-2 sm:w-auto">{actions}</div>}
    </div>
  )
}
