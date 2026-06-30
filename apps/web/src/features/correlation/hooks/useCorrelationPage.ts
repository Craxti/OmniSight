import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { useState } from 'react'
import { useI18n } from '@/context/useI18n'
import { correlationApi } from '@/shared/api'
import { omitFalsyValues } from '@/shared/api/v1Envelope'
import { downloadBlob } from '@/shared/api/client'
import type { CorrelationIngestResponse } from '@/shared/api/types'
import type { AlertRow } from '@/shared/constants'
import { queryKeys } from '@/shared/queryKeys'

const emptyAlert = (): AlertRow => ({})

export function cleanedAlerts(alerts: AlertRow[]) {
  return alerts.map((a) => omitFalsyValues(a))
}

export function useCorrelationPage() {
  const { t } = useI18n()
  const [alerts, setAlerts] = useState<AlertRow[]>([emptyAlert()])
  const [ingestResult, setIngestResult] = useState<CorrelationIngestResponse | null>(null)

  const ingestMut = useApiMutation<CorrelationIngestResponse, void>({
    mutationFn: () => correlationApi.ingest(cleanedAlerts(alerts), 'ui'),
    messages: { success: t.correlation.toastIngest, error: t.common.error },
    invalidateKeys: [queryKeys.correlation.all],
    onSuccess: (r) => setIngestResult(r),
  })

  const exportJson = () => {
    if (!ingestResult) return
    downloadBlob(
      new Blob([JSON.stringify(ingestResult, null, 2)], { type: 'application/json' }),
      'correlation-result.json',
    )
  }

  return {
    t,
    alerts,
    setAlerts,
    ingestResult,
    ingestMut,
    exportJson,
  }
}
