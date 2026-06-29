import type { ReactNode } from 'react'
import { useI18n } from '@/context/useI18n'
import { Button } from '@/components/ui'

type FormModalActionsProps = {
  onCancel: () => void
  onSubmit?: () => void
  submitLabel: string
  pending?: boolean
  submitDisabled?: boolean
  submitType?: 'button' | 'submit'
  submitTestId?: string
  children?: ReactNode
  /** Shown on the left in split layout (e.g. validation warning). */
  footerNote?: ReactNode
  layout?: 'simple' | 'split' | 'destructive'
  submitVariant?: 'primary' | 'danger'
  cancelLabel?: string
  /** Left-side action for destructive layout (e.g. delete). */
  destructiveAction?: ReactNode
}

export function FormModalActions({
  onCancel,
  onSubmit,
  submitLabel,
  pending = false,
  submitDisabled = false,
  submitType = 'button',
  submitTestId,
  children,
  footerNote,
  layout = 'simple',
  submitVariant = 'primary',
  cancelLabel,
  destructiveAction,
}: FormModalActionsProps) {
  const { t } = useI18n()

  const cancelButton = (
    <Button variant="secondary" onClick={onCancel}>
      {cancelLabel ?? t.common.cancel}
    </Button>
  )

  const submitButton = (
    <Button
      type={submitType}
      variant={submitVariant === 'danger' || layout === 'destructive' ? 'danger' : 'primary'}
      onClick={submitType === 'button' ? onSubmit : undefined}
      disabled={submitDisabled || pending}
      data-testid={submitTestId}
    >
      {submitLabel}
    </Button>
  )

  const rightButtons = (
    <>
      {children}
      {cancelButton}
      {submitButton}
    </>
  )

  if (layout === 'destructive') {
    return (
      <div className="mt-6 flex items-center justify-between gap-2">
        <div>{destructiveAction}</div>
        <div className="flex gap-2">{rightButtons}</div>
      </div>
    )
  }

  if (layout === 'split') {
    return (
      <div className="mt-6 flex flex-col items-end gap-2 sm:flex-row sm:items-center sm:justify-between">
        {footerNote ? <p className="hint hint-warning">{footerNote}</p> : <span />}
        <div className="flex gap-2">{rightButtons}</div>
      </div>
    )
  }

  return <div className="mt-6 flex justify-end gap-2">{rightButtons}</div>
}
