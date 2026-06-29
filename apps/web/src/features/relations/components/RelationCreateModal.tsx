import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { Modal } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { RelationFormFields } from '@/shared/components/RelationFormFields'
import { DEFAULT_DATA_SOURCE, type RelationType } from '@/shared/constants'
import { createRelationFormSchema } from '@/lib/forms/schemas/authSchemas'
import { defaultRelationForm } from '@/features/relations/relationsForm'

type RelationCreateForm = {
  source_ci_id: string
  target_ci_id: string
  relation_type: RelationType
  data_source: typeof DEFAULT_DATA_SOURCE
}

type Props = {
  open: boolean
  cis: { id: number; name: string }[]
  pending: boolean
  onClose: () => void
  onSubmit: (form: RelationCreateForm) => void
}

export function RelationCreateModal({ open, cis, pending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const schema = createRelationFormSchema(t)

  const {
    watch,
    setValue,
    reset,
    handleSubmit,
    formState: { errors },
  } = useForm<RelationCreateForm>({
    resolver: zodResolver(schema) as Resolver<RelationCreateForm>,
    defaultValues: defaultRelationForm,
  })

  const form = watch()

  useEffect(() => {
    if (!open) reset(defaultRelationForm)
  }, [open, reset])

  const submit = handleSubmit((data) => onSubmit(data as RelationCreateForm))

  return (
    <Modal open={open} onClose={onClose} title={t.relations.newRelation}>
      <form onSubmit={submit}>
        <RelationFormFields
          mode="select"
          sourceCiId={form.source_ci_id}
          targetCiId={form.target_ci_id}
          relationType={form.relation_type}
          dataSource={form.data_source}
          cis={cis}
          sourceError={errors.source_ci_id?.message}
          targetError={errors.target_ci_id?.message}
          onSourceChange={(source_ci_id) => setValue('source_ci_id', source_ci_id, { shouldValidate: true })}
          onTargetChange={(target_ci_id) => setValue('target_ci_id', target_ci_id, { shouldValidate: true })}
          onRelationTypeChange={(relation_type) => setValue('relation_type', relation_type as RelationType)}
          onDataSourceChange={(data_source) => setValue('data_source', data_source as typeof DEFAULT_DATA_SOURCE)}
        />
        <FormModalActions
          onCancel={onClose}
          onSubmit={submit}
          submitLabel={t.common.create}
          pending={pending}
          submitTestId="relation-submit"
        />
      </form>
    </Modal>
  )
}
