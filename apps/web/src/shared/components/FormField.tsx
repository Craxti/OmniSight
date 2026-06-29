import type { ReactNode } from 'react'
import type { FieldError } from 'react-hook-form'

type FormFieldProps = {
  label: string
  htmlFor?: string
  labelAction?: ReactNode
  error?: FieldError | string
  hint?: string
  hintTone?: 'muted' | 'warning'
  className?: string
  children: ReactNode
}

export function FormField({ label, htmlFor, labelAction, error, hint, hintTone = 'muted', className = '', children }: FormFieldProps) {
  const errorMessage = typeof error === 'string' ? error : error?.message

  return (
    <div className={className}>
      <div className="mb-1 flex items-center gap-1">
        <label className="label mb-0" htmlFor={htmlFor}>{label}</label>
        {labelAction}
      </div>
      {children}
      {hint && !errorMessage && (
        <p className={`mt-1 hint ${hintTone === 'warning' ? 'hint-warning' : ''}`}>{hint}</p>
      )}
      {errorMessage && (
        <p className="mt-1 text-xs text-error" role="alert">{errorMessage}</p>
      )}
    </div>
  )
}
