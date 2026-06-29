import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { FormField } from '@/shared/components/FormField'
import { externalIdFieldLabel } from '@/lib/domainLabels'
import type { AlertRow, ExternalIdField } from '@/shared/constants'

type Props = {
  alerts: AlertRow[]
  setAlerts: (alerts: AlertRow[]) => void
  externalIdFields: readonly string[]
  addRowLabel: string
  alertIdsTitle: string
}

export function CorrelationAlertForm({
  alerts,
  setAlerts,
  externalIdFields,
  addRowLabel,
  alertIdsTitle,
}: Props) {
  const { t } = useI18n()

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-[var(--text-primary)]">{alertIdsTitle}</h2>
        <Button variant="secondary" onClick={() => setAlerts([...alerts, {}])}>
          <Plus className="h-4 w-4" /> {addRowLabel}
        </Button>
      </div>
      <div className="space-y-3">
        {alerts.map((row, i) => (
          <div key={i} className="grid gap-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-3 md:grid-cols-7">
            {externalIdFields.map((field) => {
              const key = field as ExternalIdField
              const inputId = `correlation-alert-${i}-${field}`
              return (
                <FormField key={field} label={externalIdFieldLabel(t, field)} htmlFor={inputId}>
                  <input
                    id={inputId}
                    className="input"
                    data-testid={inputId}
                    value={row[key] || ''}
                    onChange={(e) => {
                      const next = [...alerts]
                      next[i] = { ...next[i], [key]: e.target.value } as AlertRow
                      setAlerts(next)
                    }}
                  />
                </FormField>
              )
            })}
            <div className="flex items-end">
              <Button
                variant="table-danger"
                iconOnly
                disabled={alerts.length === 1}
                onClick={() => setAlerts(alerts.filter((_, j) => j !== i))}
                aria-label={t.common.delete}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}
