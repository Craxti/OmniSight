import { useEffect, useMemo, useState } from 'react'
import { correlationApi } from '@/shared/api'
import { omitFalsyValues } from '@/shared/api/v1Envelope'
import type { AlertRow } from '@/shared/constants'
import { externalIdFieldLabel } from '@/lib/domainLabels'
import type { useI18n } from '@/context/useI18n'

type Messages = ReturnType<typeof useI18n>['t']

function rowHasIdentifier(row: AlertRow, fields: readonly string[]) {
  return fields.some((field) => {
    const value = row[field as keyof AlertRow]
    return typeof value === 'string' && value.trim().length > 0
  })
}

function describeAlertFields(alert: Record<string, string>, fields: readonly string[], t: Messages) {
  return fields
    .filter((field) => alert[field])
    .map((field) => `${externalIdFieldLabel(t, field)}=${alert[field]}`)
    .join(', ')
}

export function useCorrelationAlertWarnings(alerts: AlertRow[], externalIdFields: readonly string[], t: Messages) {
  const [checking, setChecking] = useState(false)
  const [unresolvedHints, setUnresolvedHints] = useState<string[]>([])

  const cleaned = useMemo(() => alerts.map((row) => omitFalsyValues(row)), [alerts])
  const nonEmpty = useMemo(() => cleaned.filter((row) => Object.keys(row).length > 0), [cleaned])

  const emptyRowNumbers = useMemo(
    () =>
      alerts
        .map((row, index) => (rowHasIdentifier(row, externalIdFields) ? null : index + 1))
        .filter((n): n is number => n != null),
    [alerts, externalIdFields],
  )

  useEffect(() => {
    if (nonEmpty.length === 0) {
      setUnresolvedHints([])
      setChecking(false)
      return
    }

    let cancelled = false
    const timer = window.setTimeout(() => {
      setChecking(true)
      void correlationApi
        .resolve(nonEmpty)
        .then((result) => {
          if (cancelled) return
          const hints = result.unresolved.map((item) =>
            describeAlertFields(item.alert as Record<string, string>, externalIdFields, t),
          )
          setUnresolvedHints(hints.filter(Boolean))
        })
        .catch(() => {
          if (!cancelled) setUnresolvedHints([])
        })
        .finally(() => {
          if (!cancelled) setChecking(false)
        })
    }, 450)

    return () => {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [nonEmpty, externalIdFields, t])

  const hasWarnings = emptyRowNumbers.length > 0 || unresolvedHints.length > 0 || checking

  return {
    checking,
    hasWarnings,
    emptyRowNumbers,
    unresolvedHints,
  }
}
