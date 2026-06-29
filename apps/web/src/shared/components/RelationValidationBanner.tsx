import type { RelationValidationResult } from '@/shared/api/types'

type Props = {
  validation: RelationValidationResult
  validLabel: string
  issuesLabel: string
  className?: string
}

export function RelationValidationBanner({ validation, validLabel, issuesLabel, className = '' }: Props) {
  return (
    <div
      className={`alert ${validation.valid ? 'alert-success' : 'alert-error'} ${className}`.trim()}
    >
      {validation.valid ? (
        validLabel
      ) : (
        <div>
          <span>{issuesLabel}: {validation.issues.length}</span>
          <pre className="mt-2 text-xs text-[var(--text-muted)]">{JSON.stringify(validation.issues, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
