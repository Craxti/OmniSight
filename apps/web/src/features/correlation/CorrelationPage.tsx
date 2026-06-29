import { Download, Play, Zap } from 'lucide-react'
import type { CSSProperties } from 'react'
import { PageHeader, Button, CorrelationResultSkeleton } from '@/components/ui'
import { CorrelationAlertForm } from '@/features/correlation/components/CorrelationAlertForm'
import { EmbeddedGraphView } from '@/shared/components/graph/EmbeddedGraphView'
import { useI18n } from '@/context/useI18n'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { useCorrelationPage } from '@/features/correlation/hooks/useCorrelationPage'
import { ciTypeLabel, criticalityLabel } from '@/lib/domainLabels'

export default function CorrelationPage() {
  const { t } = useI18n()
  const { externalIdFields } = useDomainConstants()
  const {
    alerts,
    setAlerts,
    ingestResult,
    ingestMut,
    correlationPayload,
    correlationGraph,
    rootCauseRootId,
    rootCauseZoneIds,
    alertResourceIds,
    correlationPathEdgeKeys,
    exportJson,
    ambiguousCount,
    staleContext,
  } = useCorrelationPage()

  return (
    <div className="space-y-6">
      <PageHeader title={t.correlation.title} subtitle={t.correlation.subtitle} />

      <div className="card p-5">
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

      {ingestResult && !ingestMut.isPending && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="card p-5">
            <h3 className="mb-3 flex items-center gap-2 font-semibold text-[var(--text-primary)]">
              <Zap className="h-4 w-4 text-warning" /> {t.correlation.result}
            </h3>
            <div className="space-y-2 text-sm text-[var(--text-muted)]">
              <div>{t.correlation.resolved}: <span className="text-[var(--text-primary)]">{ingestResult.resolve.resolved.length}</span></div>
              <div>{t.correlation.unresolved}: <span className="text-[var(--text-primary)]">{ingestResult.resolve.unresolved.length}</span></div>
              {ambiguousCount > 0 && (
                <div>{t.correlation.ambiguous}: <span className="text-warning">{ambiguousCount}</span></div>
              )}
              <div>
                {t.correlation.chainRelated}:{' '}
                <span
                  className={ingestResult.correlation?.chain_related ? 'text-success' : 'text-warning'}
                  data-testid="correlation-chain-related"
                >
                  {String(ingestResult.correlation?.chain_related ?? false)}
                </span>
              </div>
            </div>
            {staleContext && (
              <p className="alert alert-warning mt-3" data-testid="correlation-stale-context-hint">
                {t.correlation.staleContextHint}
              </p>
            )}
          </div>

          {correlationPayload?.enrichment && correlationPayload.enrichment.length > 0 && (
            <div className="card p-5">
              <h3 className="mb-3 font-semibold text-[var(--text-primary)]">{t.correlation.enrichment}</h3>
              <div className="space-y-3">
                {correlationPayload.enrichment.map((item, i) => (
                  <div key={i} className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-3 text-sm">
                    <div className="font-medium text-[var(--text-primary)]">{String(item.name ?? item.resource_id)}</div>
                    <div className="mt-1 text-xs text-[var(--text-muted)]">
                      {[
                        item.type ? ciTypeLabel(t, String(item.type)) : null,
                        item.environment ? String(item.environment) : null,
                        item.criticality ? criticalityLabel(t, String(item.criticality)) : null,
                      ].filter(Boolean).join(' · ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {correlationPayload?.potential_root_cause_zone && correlationPayload.potential_root_cause_zone.length > 0 && (
            <div className="card overflow-hidden p-5 lg:col-span-2">
              <h3 className="mb-3 font-semibold text-[var(--text-primary)]">{t.correlation.rootCauseZone}</h3>
              <ul className="space-y-1 text-sm text-[var(--text-muted)]">
                {correlationPayload.potential_root_cause_zone.map((ci) => (
                  <li key={ci.id} className="text-[var(--text-primary)]">
                    {ci.name} <span className="text-xs text-[var(--text-muted)]">({ciTypeLabel(t, String(ci.type))})</span>
                  </li>
                ))}
              </ul>
              {correlationGraph && rootCauseRootId != null && (
                <div className="mt-4 space-y-2">
                  <div className="flex flex-wrap gap-4 text-xs text-[var(--text-muted)]">
                    <span className="inline-flex items-center gap-2">
                      <span
                        className="graph-legend-swatch"
                        style={{ '--swatch-color': '#f87171' } as CSSProperties}
                        aria-hidden
                      />
                      {t.correlation.graphLegendRootCause}
                    </span>
                    <span className="inline-flex items-center gap-2">
                      <span
                        className="graph-legend-swatch"
                        style={{ '--swatch-color': '#34d399' } as CSSProperties}
                        aria-hidden
                      />
                      {t.correlation.graphLegendAlert}
                    </span>
                  </div>
                  <div
                    className="overflow-hidden rounded-lg border border-[var(--border-subtle)]"
                    data-testid="correlation-root-cause-graph"
                  >
                    <EmbeddedGraphView
                      graph={correlationGraph}
                      rootId={rootCauseRootId}
                      rootCauseIds={rootCauseZoneIds}
                      alertResourceIds={alertResourceIds}
                      pathEdgeKeys={correlationPathEdgeKeys}
                      emphasizeHighlighted
                      minHeight="28rem"
                      rootBadge={t.correlation.rootCauseBadge}
                      alertBadge={t.correlation.alertCiBadge}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="card p-5 lg:col-span-2">
            <h3 className="mb-3 font-semibold text-[var(--text-primary)]">{t.correlation.jsonTitle}</h3>
            <pre className="code-block max-h-80 overflow-auto p-3 text-xs text-[var(--text-muted)]">
              {JSON.stringify(ingestResult, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
