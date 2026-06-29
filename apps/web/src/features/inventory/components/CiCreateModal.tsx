import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { AttributeFields, schemaForType } from '@/shared/components/AttributeFields'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { FormField } from '@/shared/components/FormField'
import { Modal, Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { EnvironmentInput } from '@/shared/components/EnvironmentInput'
import { SERVER_TYPE_NAME, type Environment } from '@/shared/constants'
import { ciStatusLabel, criticalityLabel, externalIdFieldLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { CI_TEMPLATES, type CiFormState } from '@/features/inventory/inventoryForm'
import { useDuplicateWarnings } from '@/features/inventory/hooks/useDuplicateWarnings'
import { ciFormSchemaDefaults, createCiFormSchema } from '@/lib/forms/schemas/ciFormSchema'

type CiType = { id: number; name: string; attribute_schema?: unknown }

type Props = {
  open: boolean
  types: CiType[] | undefined
  isPending: boolean
  onClose: () => void
  onSubmit: (form: CiFormState) => void
}

export function CiCreateModal({ open, types, isPending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const { ciStatuses, criticalityLevels, externalIdFields } = useDomainConstants()
  const schema = createCiFormSchema(t)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<CiFormState>({
    resolver: zodResolver(schema) as Resolver<CiFormState>,
    defaultValues: ciFormSchemaDefaults,
  })

  const form = watch()
  const { dupWarnings, ipFormatError, getExternalHint } = useDuplicateWarnings(open, form, t)
  const typeSchema = schemaForType(types, form.type_name)
  const showHostnameHint = form.type_name === SERVER_TYPE_NAME && !form.attributes.hostname?.trim()

  useEffect(() => {
    if (!open) reset(ciFormSchemaDefaults)
  }, [open, reset])

  const applyTemplate = (name: string) => {
    const tpl = CI_TEMPLATES[name]
    if (!tpl) return
    reset({ ...form, ...tpl, attributes: { ...tpl.attributes } })
  }

  const submit = handleSubmit((data) => {
    if (dupWarnings.name) return
    onSubmit(data as CiFormState)
  })

  return (
    <Modal open={open} onClose={onClose} title={t.inventory.newCi} wide>
      <div className="mb-4 flex flex-wrap gap-2">
        {Object.keys(CI_TEMPLATES).map((tpl) => (
          <Button key={tpl} variant="secondary" className="text-xs" onClick={() => applyTemplate(tpl)}>
            {t.common.template}: {tpl}
          </Button>
        ))}
      </div>
      <form onSubmit={submit} className="grid gap-3 md:grid-cols-2">
        <FormField
          label={t.inventory.nameRequired}
          htmlFor="ci-name"
          error={errors.name?.message || dupWarnings.name}
          className="md:col-span-2"
        >
          <input
            id="ci-name"
            className={`input ${dupWarnings.name ? 'border-amber-500/60' : ''}`}
            {...register('name')}
            aria-invalid={!!dupWarnings.name || !!errors.name}
          />
        </FormField>
        <FormField label={t.inventory.typeRequired} error={errors.type_name?.message}>
          <select className="input" {...register('type_name')}>
            {(types || []).map((typeOpt) => <option key={typeOpt.id} value={typeOpt.name}>{typeOpt.name}</option>)}
          </select>
        </FormField>
        <FormField label={t.inventory.colStatus} error={errors.status?.message}>
          <select className="input" {...register('status')}>
            {ciStatuses.map((s) => <option key={s} value={s}>{ciStatusLabel(t, s)}</option>)}
          </select>
        </FormField>
        <FormField label={t.inventory.criticalityRequired} error={errors.criticality?.message}>
          <select className="input" {...register('criticality')}>
            {criticalityLevels.map((s) => <option key={s} value={s}>{criticalityLabel(t, s)}</option>)}
          </select>
        </FormField>
        <FormField label={t.inventory.environmentRequired} htmlFor="ci-environment" error={errors.environment?.message} hint={t.inventory.environmentHint}>
          <EnvironmentInput
            id="ci-environment"
            value={form.environment}
            onChange={(environment) => setValue('environment', environment as Environment, { shouldValidate: true })}
            data-testid="ci-environment"
          />
        </FormField>
        <FormField label={t.inventory.ownerRequired} htmlFor="ci-owner" error={errors.owner?.message}>
          <input id="ci-owner" className="input" {...register('owner')} />
        </FormField>
        <FormField label={t.inventory.team}>
          <input className="input" {...register('team')} />
        </FormField>
        <FormField label={t.inventory.description} className="md:col-span-2">
          <textarea className="input min-h-[60px]" {...register('description')} />
        </FormField>
        <div className="md:col-span-2 border-t border-[var(--border-subtle)] pt-3"><span className="label">{t.inventory.externalIds}</span></div>
        {showHostnameHint && (
          <p className="hint hint-warning md:col-span-2" role="note">{t.inventory.hintServerHostname}</p>
        )}
        {externalIdFields.map((field) => {
          const hint = getExternalHint(field as 'hostname' | 'ip')
          const isIpError = field === 'ip' && !!ipFormatError
          return (
          <FormField
            key={field}
            label={externalIdFieldLabel(t, field)}
            htmlFor={`ci-ext-${field}`}
            error={isIpError ? ipFormatError : undefined}
            hint={!isIpError && hint ? hint : undefined}
            hintTone={hint && !isIpError ? 'warning' : 'muted'}
          >
            <input
              id={`ci-ext-${field}`}
              className={`input ${isIpError ? 'border-red-500/60' : ''}`}
              value={form.attributes[field] || ''}
              onChange={(e) => setValue('attributes', { ...form.attributes, [field]: e.target.value }, { shouldValidate: true })}
              aria-invalid={isIpError}
            />
          </FormField>
          )
        })}
        <div className="md:col-span-2 border-t border-[var(--border-subtle)] pt-3"><span className="label">{t.inventory.typeAttrs}</span></div>
        <div className="md:col-span-2">
          <AttributeFields
            schema={typeSchema}
            values={form.attributes}
            onChange={(attributes) => setValue('attributes', attributes, { shouldValidate: true })}
          />
        </div>
        {dupWarnings.name && (
          <p className="alert alert-warning md:col-span-2" role="alert">{t.inventory.errDupName}</p>
        )}
        <div className="md:col-span-2">
          <FormModalActions
            onCancel={onClose}
            onSubmit={submit}
            submitLabel={t.common.create}
            pending={isPending}
            submitDisabled={!!dupWarnings.name || !!ipFormatError}
            submitTestId="ci-submit"
          />
        </div>
      </form>
    </Modal>
  )
}
