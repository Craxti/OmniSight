import { Download, Play } from 'lucide-react'
import { PageHeader, Button, CorrelationResultSkeleton } from '@/components/ui'
import { CorrelationAlertForm } from '@/features/correlation/components/CorrelationAlertForm'
import { CorrelationIngestJournal } from '@/features/correlation/components/CorrelationIngestJournal'
import { CorrelationIngestResultView } from '@/features/correlation/components/CorrelationIngestResultView'
import { CorrelationIngestWarnings } from '@/features/correlation/components/CorrelationIngestWarnings'
import { OnboardingHint } from '@/shared/components/OnboardingHint'
import { useI18n } from '@/context/useI18n'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { useCorrelationPage } from '@/features/correlation/hooks/useCorrelationPage'

export default function CorrelationPage() {
  const { t } = useI18n()
  const { externalIdFields } = useDomainConstants()
  const { alerts, setAlerts, ingestResult, ingestMut, exportJson } = useCorrelationPage()

  return (
    <div className="space-y-6">
      <PageHeader title={t.correlation.title} subtitle={t.correlation.subtitle} />

      <OnboardingHint storageKey="onboarding-correlation" title={t.correlation.onboardingTitle}>
        <ol>
          <li>{t.correlation.onboardingStep1}</li>
          <li>{t.correlation.onboardingStep2}</li>
          <li>{t.correlation.onboardingStep3}</li>
        </ol>
      </OnboardingHint>

      <div className="card p-5">
        <CorrelationIngestJournal />
      </div>

      <div className="card p-5">
        <h2 className="mb-4 font-semibold text-[var(--text-primary)]">{t.correlation.manualIngestTitle}</h2>
        <p className="mb-4 text-sm text-[var(--text-muted)]">{t.correlation.manualIngestHint}</p>
        <CorrelationIngestWarnings alerts={alerts} externalIdFields={externalIdFields} />
        <CorrelationAlertForm
          alerts={alerts}
          setAlerts={setAlerts}
          externalIdFields={externalIdFields}
          addRowLabel={t.correlation.addRow}
          alertIdsTitle={t.correlation.alertIds}
        />
        <div className="mt-4 flex flex-wrap gap-2">
          <Button
            variant="primary"
            onClick={() => ingestMut.mutate(undefined)}
            disabled={ingestMut.isPending}
            data-testid="correlation-ingest"
          >
            <Play className="h-4 w-4" /> {t.correlation.ingest}
          </Button>
          {ingestResult && (
            <Button variant="secondary" onClick={exportJson}>
              <Download className="h-4 w-4" /> {t.correlation.exportJson}
            </Button>
          )}
        </div>
      </div>

      {ingestMut.isPending && <CorrelationResultSkeleton />}

      {ingestResult && !ingestMut.isPending && <CorrelationIngestResultView ingestResult={ingestResult} />}
    </div>
  )
}
