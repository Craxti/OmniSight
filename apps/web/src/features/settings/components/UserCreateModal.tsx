import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { Modal } from '@/components/ui'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { FormField } from '@/shared/components/FormField'
import { PasswordField } from '@/features/settings/components/PasswordField'
import { useI18n } from '@/context/useI18n'
import { generatePassword } from '@/lib/password'
import { createUserCreateSchema, type UserCreateValues } from '@/lib/forms/schemas/settingsSchemas'

export type UserCreateForm = UserCreateValues

type Props = {
  open: boolean
  pending: boolean
  onClose: () => void
  onSubmit: (form: UserCreateForm) => void
}

const defaultValues: UserCreateForm = { email: '', role: 'viewer', password: '' }

export function UserCreateModal({ open, pending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const schema = createUserCreateSchema(t)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<UserCreateForm>({
    resolver: zodResolver(schema) as Resolver<UserCreateForm>,
    defaultValues,
  })

  const password = watch('password')

  useEffect(() => {
    if (open) {
      reset({ email: '', role: 'viewer', password: generatePassword() })
    }
  }, [open, reset])

  const submit = handleSubmit((data) => onSubmit(data))

  return (
    <Modal open={open} onClose={onClose} title={t.settings.addUserTitle}>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-xs text-[var(--text-muted)]">{t.settings.createUserHint}</p>
        <FormField label="Email" error={errors.email?.message}>
          <input
            className="input"
            type="email"
            autoFocus
            placeholder={t.settings.emailPlaceholder}
            {...register('email')}
          />
        </FormField>
        <FormField label={t.settings.colRole} error={errors.role?.message}>
          <select className="input" {...register('role')}>
            <option value="viewer">{t.settings.roles.viewer}</option>
            <option value="editor">{t.settings.roles.editor}</option>
            <option value="admin">{t.settings.roles.admin}</option>
          </select>
        </FormField>
        <FormField label={t.settings.password} error={errors.password?.message}>
          <PasswordField
            label=""
            value={password}
            onChange={(value) => setValue('password', value, { shouldValidate: true })}
            required
          />
        </FormField>
        <FormModalActions
          onCancel={onClose}
          submitLabel={t.settings.addUser}
          pending={pending}
          submitType="submit"
        />
      </form>
    </Modal>
  )
}
