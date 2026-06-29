import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { Modal } from '@/components/ui'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { FormField } from '@/shared/components/FormField'
import { useI18n } from '@/context/useI18n'
import {
  createRelationTypeFormSchema,
  type RelationTypeFormValues,
} from '@/lib/forms/schemas/relationTypeSchemas'

export type RelationTypeFormState = RelationTypeFormValues

type Props = {
  open: boolean
  initial: RelationTypeFormState | null
  pending: boolean
  onClose: () => void
  onSubmit: (form: RelationTypeFormState) => void
}

export function RelationTypeFormModal({ open, initial, pending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const schema = createRelationTypeFormSchema(t)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<RelationTypeFormState>({
    resolver: zodResolver(schema) as Resolver<RelationTypeFormState>,
    defaultValues: { name: '', description: '' },
  })

  useEffect(() => {
    if (open && initial) {
      reset(initial)
    }
  }, [open, initial, reset])

  const submit = handleSubmit((data) => onSubmit(data))
  const isOfficial = initial?.isOfficial

  if (!open || !initial) return null

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={initial.id ? t.settings.editRelationType : t.settings.newRelationType}
    >
      <form onSubmit={submit} className="space-y-3">
        <FormField label={t.settings.relationTypeKey} hint={t.settings.relationTypeKeyHint} error={errors.name?.message}>
          <input className="input font-mono text-sm" readOnly={isOfficial} {...register('name')} />
        </FormField>
        <FormField label={t.settings.typeDescription} error={errors.description?.message}>
          <input className="input" {...register('description')} />
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
