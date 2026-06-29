import type { ReactNode } from 'react'
import { Modal } from '@/components/ui'
import { FormModalActions } from '@/shared/components/FormModalActions'

type ConfirmDialogProps = {
  open: boolean
  title: string
  message: ReactNode
  confirmLabel: string
  onClose: () => void
  onConfirm: () => void
  pending?: boolean
  confirmTestId?: string
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  onClose,
  onConfirm,
  pending = false,
  confirmTestId,
}: ConfirmDialogProps) {
  return (
    <Modal open={open} onClose={onClose} title={title}>
      <div className="space-y-4">
        <div className="text-sm text-[var(--text-muted)]">{message}</div>
        <FormModalActions
          onCancel={onClose}
          onSubmit={onConfirm}
          submitLabel={confirmLabel}
          submitVariant="danger"
          pending={pending}
          submitTestId={confirmTestId}
        />
      </div>
    </Modal>
  )
}
