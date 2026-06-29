import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { Modal } from '@/components/ui'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { FormField } from '@/shared/components/FormField'
import { PasswordField } from '@/features/settings/components/PasswordField'
import { useI18n } from '@/context/useI18n'
import { generatePassword } from '@/lib/password'
import { createPasswordResetSchema } from '@/lib/forms/schemas/settingsSchemas'

type PasswordResetValues = { password: string }

type Props = {
  open: boolean
  email: string
  pending: boolean
  onClose: () => void
  onSubmit: (password: string) => void
}

export function PasswordResetModal({ open, email, pending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const schema = createPasswordResetSchema(t)

  const {
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<PasswordResetValues>({
    resolver: zodResolver(schema) as Resolver<PasswordResetValues>,
    defaultValues: { password: '' },
  })

  const password = watch('password')

  useEffect(() => {
    if (open) {
      reset({ password: generatePassword() })
    }
  }, [open, reset])

  const submit = handleSubmit(({ password: nextPassword }) => onSubmit(nextPassword))

  return (
    <Modal open={open} onClose={onClose} title={t.settings.resetPasswordTitle}>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-sm text-[var(--text-muted)]">{email}</p>
        <p className="text-xs text-[var(--text-muted)]">{t.settings.resetPasswordHint}</p>
        <FormField label={t.settings.newPassword} error={errors.password?.message}>
          <PasswordField
            label=""
            value={password}
            onChange={(value) => setValue('password', value, { shouldValidate: true })}
            autoFocus
          />
        </FormField>
        <FormModalActions
          onCancel={onClose}
          submitLabel={t.common.save}
          pending={pending}
          submitType="submit"
        />
      </form>
    </Modal>
  )
}
