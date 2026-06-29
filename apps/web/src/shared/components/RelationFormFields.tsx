import { useI18n } from '@/context/useI18n'
import { FormField } from '@/shared/components/FormField'
import { relationTypeLabel, relationStatusLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { useRelationTypes } from '@/shared/hooks/useRelationTypes'

export type CiOption = { id: number; name: string }

type BaseProps = {
  relationType: string
  dataSource: string
  onRelationTypeChange: (value: string) => void
  onDataSourceChange: (value: string) => void
}

type SelectEndpointsProps = BaseProps & {
  mode: 'select'
  sourceCiId: string
  targetCiId: string
  cis: CiOption[]
  sourceError?: string
  targetError?: string
  onSourceChange: (value: string) => void
  onTargetChange: (value: string) => void
}

type ReadonlyEndpointsProps = BaseProps & {
  mode: 'readonly'
  sourceCiId: number
  targetCiId: number
  ciDisplay: (ciId: number) => string
}

type EditWithEndpointsProps = BaseProps & {
  mode: 'edit-with-endpoints'
  sourceCiId: number
  targetCiId: number
  status: string
  ciDisplay: (ciId: number) => string
  onStatusChange: (value: string) => void
}

type EditFieldsProps = BaseProps & {
  mode: 'edit'
  status: string
  onStatusChange: (value: string) => void
}

type FilterTypeProps = {
  mode: 'filter-type'
  relationType: string
  onRelationTypeChange: (value: string) => void
  includeAllOption?: boolean
  testId?: string
}

type FilterStatusProps = {
  mode: 'filter-status'
  status: string
  onStatusChange: (value: string) => void
  includeAllOption?: boolean
  testId?: string
}

export type RelationFormFieldsProps =
  | SelectEndpointsProps
  | ReadonlyEndpointsProps
  | EditWithEndpointsProps
  | EditFieldsProps
  | FilterTypeProps
  | FilterStatusProps

function RelationTypeSelect({
  value,
  onChange,
  includeAllOption,
  allLabel,
  testId,
}: {
  value: string
  onChange: (value: string) => void
  includeAllOption?: boolean
  allLabel?: string
  testId?: string
}) {
  const { t } = useI18n()
  const { relationTypes } = useDomainConstants()
  const { data: relationTypeDefs } = useRelationTypes()
  const labelFor = (key: string) => {
    const custom = relationTypeDefs?.find((row) => row.name === key)?.description
    return relationTypeLabel(t, key, custom)
  }
  return (
    <select className="input" value={value} data-testid={testId} onChange={(e) => onChange(e.target.value)}>
      {includeAllOption && <option value="">{allLabel}</option>}
      {relationTypes.map((rt) => (
        <option key={rt} value={rt}>
          {labelFor(rt)}
        </option>
      ))}
    </select>
  )
}

function RelationStatusSelect({
  value,
  onChange,
  includeAllOption,
  allLabel,
  testId,
}: {
  value: string
  onChange: (value: string) => void
  includeAllOption?: boolean
  allLabel?: string
  testId?: string
}) {
  const { t } = useI18n()
  const { relationStatuses } = useDomainConstants()
  return (
    <select className="input" value={value} data-testid={testId} onChange={(e) => onChange(e.target.value)}>
      {includeAllOption && <option value="">{allLabel}</option>}
      {relationStatuses.map((s) => (
        <option key={s} value={s}>
          {relationStatusLabel(t, s)}
        </option>
      ))}
    </select>
  )
}

export function RelationFormFields(props: RelationFormFieldsProps) {
  const { t } = useI18n()

  if (props.mode === 'filter-type') {
    return (
      <FormField label={t.relations.relationType}>
        <RelationTypeSelect
          value={props.relationType}
          onChange={props.onRelationTypeChange}
          includeAllOption={props.includeAllOption ?? true}
          allLabel={t.relations.allRelationTypes}
          testId={props.testId}
        />
      </FormField>
    )
  }

  if (props.mode === 'filter-status') {
    return (
      <FormField label={t.relations.colStatus}>
        <RelationStatusSelect
          value={props.status}
          onChange={props.onStatusChange}
          includeAllOption={props.includeAllOption ?? true}
          allLabel={t.relations.allStatuses}
          testId={props.testId}
        />
      </FormField>
    )
  }

  if (props.mode === 'select') {
    return (
      <div className="space-y-3">
        <FormField label={t.relations.source} htmlFor="rel-source" error={props.sourceError}>
          <select
            id="rel-source"
            className={`input ${props.sourceError ? 'border-red-500/60' : ''}`}
            value={props.sourceCiId}
            onChange={(e) => props.onSourceChange(e.target.value)}
            aria-invalid={!!props.sourceError}
          >
            <option value="">{t.common.selectPlaceholder}</option>
            {props.cis.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label={t.relations.target} htmlFor="rel-target" error={props.targetError}>
          <select
            id="rel-target"
            className={`input ${props.targetError ? 'border-red-500/60' : ''}`}
            value={props.targetCiId}
            onChange={(e) => props.onTargetChange(e.target.value)}
            aria-invalid={!!props.targetError}
          >
            <option value="">{t.common.selectPlaceholder}</option>
            {props.cis.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label={t.relations.relationType}>
          <RelationTypeSelect value={props.relationType} onChange={props.onRelationTypeChange} />
        </FormField>
        <FormField label={t.relations.colDataSource}>
          <input className="input" value={props.dataSource} onChange={(e) => props.onDataSourceChange(e.target.value)} />
        </FormField>
      </div>
    )
  }

  if (props.mode === 'readonly') {
    return (
      <div className="space-y-3">
        <FormField label={t.relations.source} hint={`ID: ${props.sourceCiId}`}>
          <input className="input" value={props.ciDisplay(props.sourceCiId)} readOnly />
        </FormField>
        <FormField label={t.relations.target} hint={`ID: ${props.targetCiId}`}>
          <input className="input" value={props.ciDisplay(props.targetCiId)} readOnly />
        </FormField>
        <FormField label={t.relations.relationType}>
          <RelationTypeSelect value={props.relationType} onChange={props.onRelationTypeChange} />
        </FormField>
        <FormField label={t.relations.colDataSource}>
          <input className="input" value={props.dataSource} onChange={(e) => props.onDataSourceChange(e.target.value)} />
        </FormField>
      </div>
    )
  }

  if (props.mode === 'edit-with-endpoints') {
    return (
      <div className="space-y-3">
        <FormField label={t.relations.source} hint={`ID: ${props.sourceCiId}`}>
          <input className="input" value={props.ciDisplay(props.sourceCiId)} readOnly />
        </FormField>
        <FormField label={t.relations.target} hint={`ID: ${props.targetCiId}`}>
          <input className="input" value={props.ciDisplay(props.targetCiId)} readOnly />
        </FormField>
        <FormField label={t.relations.relationType}>
          <RelationTypeSelect value={props.relationType} onChange={props.onRelationTypeChange} />
        </FormField>
        <FormField label={t.relations.colStatus}>
          <RelationStatusSelect value={props.status} onChange={props.onStatusChange} />
        </FormField>
        <FormField label={t.relations.colDataSource}>
          <input className="input" value={props.dataSource} onChange={(e) => props.onDataSourceChange(e.target.value)} />
        </FormField>
      </div>
    )
  }

  if (props.mode === 'edit') {
    return (
      <div className="space-y-3">
        <FormField label={t.relations.relationType}>
          <RelationTypeSelect value={props.relationType} onChange={props.onRelationTypeChange} />
        </FormField>
        <FormField label={t.relations.colStatus}>
          <RelationStatusSelect value={props.status} onChange={props.onStatusChange} />
        </FormField>
        <FormField label={t.relations.colDataSource}>
          <input className="input" value={props.dataSource} onChange={(e) => props.onDataSourceChange(e.target.value)} />
        </FormField>
      </div>
    )
  }

  return null
}
