import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { Modal } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { fmt } from '@/i18n/messages'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { RelationFormFields } from '@/shared/components/RelationFormFields'
import { createRelationEditSchema } from '@/lib/forms/schemas/settingsSchemas'

export type RelationEditState = {
  id: number
  relation_type: string
  status: string
  data_source: string
}

type Props = {
  editRel: RelationEditState | null
  pending: boolean
  onClose: () => void
  onSubmit: (rel: RelationEditState) => void
}

export function RelationEditModal({ editRel, pending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const schema = createRelationEditSchema(t)

  const {
    watch,
    setValue,
    reset,
    handleSubmit,
    formState: { errors },
  } = useForm<RelationEditState>({
    resolver: zodResolver(schema) as Resolver<RelationEditState>,
  })

  const form = watch()

  useEffect(() => {
    if (editRel) reset(editRel)
  }, [editRel, reset])

  const submit = handleSubmit((data) => onSubmit(data))

  return (
    <Modal
      open={editRel !== null}
      onClose={onClose}
      title={editRel ? fmt(t.relations.editTitle, { id: editRel.id }) : ''}
    >
      {editRel && (
        <form onSubmit={submit}>
          <RelationFormFields
            mode="edit"
            relationType={form.relation_type}
            status={form.status}
            dataSource={form.data_source}
            onRelationTypeChange={(relation_type) => setValue('relation_type', relation_type, { shouldValidate: true })}
            onStatusChange={(status) => setValue('status', status, { shouldValidate: true })}
            onDataSourceChange={(data_source) => setValue('data_source', data_source, { shouldValidate: true })}
          />
          {(errors.relation_type || errors.status || errors.data_source) && (
            <p className="mt-2 text-xs text-error" role="alert">
              {errors.relation_type?.message || errors.status?.message || errors.data_source?.message}
            </p>
          )}
          <FormModalActions
            onCancel={onClose}
            onSubmit={submit}
            submitLabel={t.common.save}
            pending={pending}
          />
        </form>
      )}
    </Modal>
  )
}
