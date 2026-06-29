import { zodResolver } from '@hookform/resolvers/zod'
import { Braces, LayoutList } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { Modal } from '@/components/ui'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { FormField } from '@/shared/components/FormField'
import { useI18n } from '@/context/useI18n'
import { createCiTypeFormSchema, type CiTypeFormValues } from '@/lib/forms/schemas/settingsSchemas'
import {
  buildSchemaJson,
  hasDuplicateSchemaKeys,
  parseSchemaFields,
  type SchemaFieldDef,
} from '@/lib/ciTypeSchema'
import { SchemaFieldsEditor } from '@/features/settings/components/SchemaFieldsEditor'

export type CiTypeFormState = CiTypeFormValues

type EditorMode = 'visual' | 'json'

type Props = {
  open: boolean
  initial: CiTypeFormState | null
  pending: boolean
  onClose: () => void
  onSubmit: (form: CiTypeFormState) => void
}

export function CiTypeFormModal({ open, initial, pending, onClose, onSubmit }: Props) {
  const { t } = useI18n()
  const schema = createCiTypeFormSchema(t)
  const [editorMode, setEditorMode] = useState<EditorMode>('visual')
  const [fields, setFields] = useState<SchemaFieldDef[]>([])
  const [modeError, setModeError] = useState<string | null>(null)
  const [duplicateError, setDuplicateError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<CiTypeFormState>({
    resolver: zodResolver(schema) as Resolver<CiTypeFormState>,
    defaultValues: { name: '', description: '', schemaJson: '{\n  "properties": {}\n}' },
  })

  const schemaJson = watch('schemaJson')

  useEffect(() => {
    if (open && initial) {
      reset(initial)
      const parsed = parseSchemaFields(initial.schemaJson)
      setFields(parsed.fields)
      setEditorMode('visual')
      setModeError(null)
      setDuplicateError(null)
    }
  }, [open, initial, reset])

  const syncFieldsToJson = (nextFields: SchemaFieldDef[]) => {
    setFields(nextFields)
    setValue('schemaJson', buildSchemaJson(nextFields), { shouldValidate: true })
    setDuplicateError(
      hasDuplicateSchemaKeys(nextFields) ? t.settings.schemaErrDuplicateKey : null,
    )
  }

  const switchEditorMode = (mode: EditorMode) => {
    if (mode === editorMode) return
    if (mode === 'visual') {
      const parsed = parseSchemaFields(schemaJson)
      if (parsed.error) {
        setModeError(t.settings.schemaErrSwitchVisual)
        return
      }
      setFields(parsed.fields)
      setModeError(null)
    } else {
      setValue('schemaJson', buildSchemaJson(fields), { shouldValidate: true })
      setModeError(null)
    }
    setEditorMode(mode)
  }

  const submit = handleSubmit((data) => {
    const payload = { ...data }
    if (editorMode === 'visual') {
      if (hasDuplicateSchemaKeys(fields)) {
        setDuplicateError(t.settings.schemaErrDuplicateKey)
        return
      }
      payload.schemaJson = buildSchemaJson(fields)
    }
    onSubmit(payload)
  })

  if (!open || !initial) return null

  return (
    <Modal open={open} onClose={onClose} title={initial.id ? t.settings.editType : t.settings.newTypeCi} wide>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <FormField label={t.settings.typeName} error={errors.name?.message}>
            <input className="input" {...register('name')} />
          </FormField>
          <FormField label={t.settings.typeDescription} error={errors.description?.message}>
            <input className="input" {...register('description')} />
          </FormField>
        </div>

        <div className="space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="label">{t.settings.typeSchema}</span>
            <div className="settings-tabs !inline-flex !p-0.5" role="tablist" aria-label={t.settings.typeSchema}>
              <button
                type="button"
                role="tab"
                aria-selected={editorMode === 'visual'}
                data-active={editorMode === 'visual'}
                className="!px-3 !py-1.5 text-xs"
                onClick={() => switchEditorMode('visual')}
              >
                <LayoutList className="h-3.5 w-3.5" aria-hidden />
                {t.settings.typeSchemaVisual}
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={editorMode === 'json'}
                data-active={editorMode === 'json'}
                className="!px-3 !py-1.5 text-xs"
                onClick={() => switchEditorMode('json')}
              >
                <Braces className="h-3.5 w-3.5" aria-hidden />
                {t.settings.typeSchemaJson}
              </button>
            </div>
          </div>

          {editorMode === 'visual' ? (
            <SchemaFieldsEditor
              fields={fields}
              onChange={syncFieldsToJson}
              duplicateError={duplicateError ?? undefined}
            />
          ) : (
            <FormField label={t.settings.typeSchemaJson} error={errors.schemaJson?.message || modeError || undefined}>
              <textarea
                className="input min-h-[220px] font-mono text-xs leading-relaxed"
                {...register('schemaJson')}
                spellCheck={false}
              />
            </FormField>
          )}
        </div>

        <FormModalActions
          onCancel={onClose}
          submitLabel={t.common.save}
          pending={pending}
          submitType="submit"
          submitDisabled={!!duplicateError}
        />
      </form>
    </Modal>
  )
}
