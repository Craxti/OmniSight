import { useI18n } from '@/context/useI18n'
import { EnvironmentInput } from '@/shared/components/EnvironmentInput'
import { FormField } from '@/shared/components/FormField'
import { ciStatusLabel, criticalityLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import type { CiStatus, CriticalityLevel, Environment } from '@/shared/constants'

export type CiEditFormState = {
  name: string
  description: string
  status: string
  criticality: string
  environment: string
  owner: string
  team: string
}

type Props = {
  form: CiEditFormState
  onChange: (form: CiEditFormState) => void
}

export function CiEditForm({ form, onChange }: Props) {
  const { t } = useI18n()
  const { ciStatuses, criticalityLevels } = useDomainConstants()

  return (
    <div className="card space-y-3 p-5 lg:col-span-2">
      <FormField label={t.inventory.nameRequired} htmlFor="ci-edit-name">
        <input
          id="ci-edit-name"
          className="input"
          value={form.name}
          onChange={(e) => onChange({ ...form, name: e.target.value })}
        />
      </FormField>
      <FormField label={t.inventory.colStatus}>
        <select
          className="input"
          value={form.status}
          onChange={(e) => onChange({ ...form, status: e.target.value as CiStatus })}
        >
          {ciStatuses.map((s) => (
            <option key={s} value={s}>{ciStatusLabel(t, s)}</option>
          ))}
        </select>
      </FormField>
      <FormField label={t.inventory.criticalityRequired}>
        <select
          className="input"
          value={form.criticality}
          onChange={(e) => onChange({ ...form, criticality: e.target.value as CriticalityLevel })}
        >
          <option value="">{t.nav.noResults}</option>
          {criticalityLevels.map((s) => (
            <option key={s} value={s}>{criticalityLabel(t, s)}</option>
          ))}
        </select>
      </FormField>
      <FormField label={t.inventory.environmentRequired} htmlFor="ci-edit-environment">
        <EnvironmentInput
          id="ci-edit-environment"
          value={form.environment}
          onChange={(environment) => onChange({ ...form, environment: environment as Environment })}
        />
      </FormField>
      <FormField label={t.inventory.ownerRequired} htmlFor="ci-edit-owner">
        <input
          id="ci-edit-owner"
          className="input"
          value={form.owner}
          onChange={(e) => onChange({ ...form, owner: e.target.value })}
        />
      </FormField>
      <FormField label={t.inventory.team}>
        <input
          className="input"
          value={form.team}
          onChange={(e) => onChange({ ...form, team: e.target.value })}
        />
      </FormField>
      <FormField label={t.inventory.description}>
        <textarea
          className="input min-h-[60px]"
          value={form.description}
          onChange={(e) => onChange({ ...form, description: e.target.value })}
        />
      </FormField>
    </div>
  )
}
