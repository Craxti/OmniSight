import { Image, Maximize2, Network, Radar, RotateCcw, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { relationTypeLabel } from '@/lib/domainLabels'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { RelationValidationBanner } from '@/shared/components/RelationValidationBanner'
import { FormField } from '@/shared/components/FormField'
import type { CI, RelationValidationResult } from '@/shared/api/types'
import { GRAPH_NODE_MARKER_COLORS } from '@/lib/graphVisuals'
import { CiRootPicker } from '@/features/graph/components/CiRootPicker'

type ImpactItem = { id: number; name: string; criticality?: string | null }

type Props = {
  rootId: string
  isOverview: boolean
  onRootChange: (id: string) => void
  onShowOverview: () => void
  depth: number
  onDepthChange: (depth: number) => void
  relationFilter: string
  onRelationFilterChange: (value: string) => void
  nodeCount: number
  edgeCount: number
  canExport: boolean
  onFit: () => void
  onRelayout: () => void
  onExport: () => void
  businessPath: CI[]
  impactedServices: ImpactItem[]
  components: CI[]
  isBusinessServiceRoot: boolean
  validation: RelationValidationResult | null | undefined
  validating: boolean
  onValidate: () => void
  canEdit?: boolean
  onAutodiscover?: () => void
}

function AnalysisList({
  title,
  items,
  empty,
  markerColor,
}: {
  title: string
  items: Array<{ id: number; name: string; hint?: string }>
  empty: string
  markerColor: string
}) {
  return (
    <div>
      <div className="text-caption mb-1.5 font-medium uppercase tracking-wide text-[var(--text-muted)]">{title}</div>
      {items.length === 0 ? (
        <p className="text-xs text-[var(--text-muted)]">{empty}</p>
      ) : (
        <ul className="space-y-1">
          {items.map((item) => (
            <li key={item.id} className="flex items-start gap-1.5 text-xs text-[var(--text-primary)]">
              <span
                className="mt-1.5 h-2 w-2 shrink-0 rounded-full ring-1 ring-[var(--border-subtle)]"
                style={{ backgroundColor: markerColor, boxShadow: `0 0 4px ${markerColor}` }}
              />
              <span>
                {item.name}
                {item.hint ? <span className="text-[var(--text-muted)]"> · {item.hint}</span> : null}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function GraphMapSidebar({
  rootId,
  isOverview,
  onRootChange,
  onShowOverview,
  depth,
  onDepthChange,
  relationFilter,
  onRelationFilterChange,
  nodeCount,
  edgeCount,
  canExport,
  onFit,
  onRelayout,
  onExport,
  businessPath,
  impactedServices,
  components,
  isBusinessServiceRoot,
  validation,
  validating,
  onValidate,
  canEdit,
  onAutodiscover,
}: Props) {
  const { t } = useI18n()
  const { relationTypes } = useDomainConstants()
  const hasRoot = Boolean(rootId)

  return (
    <aside className="graph-sidebar flex h-full min-h-0 w-80 shrink-0 flex-col border-r border-[var(--border-subtle)] bg-[var(--bg-card)]">
      <div className="border-b border-[var(--border-subtle)] p-4">
        <h2 className="text-base font-semibold text-[var(--text-primary)]">{t.graph.title}</h2>
        <p className="mt-1 text-xs text-[var(--text-muted)]">
          {isOverview ? t.graph.overviewSubtitle : t.graph.subtitle}
        </p>
      </div>

      <div className="relative z-40 shrink-0 overflow-visible border-b border-[var(--border-subtle)] p-4 pb-5">
        <CiRootPicker value={rootId} onChange={onRootChange} />
        {hasRoot ? (
          <Button
            variant="secondary"
            className="mt-2 w-full justify-start text-xs"
            onClick={onShowOverview}
            data-testid="graph-show-overview"
          >
            <Network className="h-3.5 w-3.5" /> {t.graph.showOverview}
          </Button>
        ) : null}
      </div>

      <div className="relative z-0 flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-4">
        {!isOverview ? (
          <FormField label={t.graph.depth} htmlFor="graph-depth">
            <input
              id="graph-depth"
              className="input"
              type="number"
              min={1}
              max={10}
              value={depth}
              onChange={(e) => onDepthChange(Number(e.target.value))}
            />
          </FormField>
        ) : null}

        <FormField label={t.graph.relationType} htmlFor="graph-relation">
          <select
            id="graph-relation"
            className="input"
            value={relationFilter}
            onChange={(e) => onRelationFilterChange(e.target.value)}
          >
            <option value="">{t.common.all}</option>
            {relationTypes.map((rt) => (
              <option key={rt} value={rt}>{relationTypeLabel(t, rt)}</option>
            ))}
          </select>
        </FormField>

        {hasRoot ? (
          <div className="space-y-3 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-3">
            <AnalysisList
              title={t.graph.businessPathPanel}
              items={businessPath.map((ci) => ({ id: ci.id, name: ci.name, hint: ci.type || undefined }))}
              empty={t.graph.businessPathEmpty}
              markerColor={GRAPH_NODE_MARKER_COLORS.businessPath}
            />
            <AnalysisList
              title={t.graph.impactPanel}
              items={impactedServices.map((s) => ({
                id: s.id,
                name: s.name,
                hint: s.criticality ?? undefined,
              }))}
              empty={t.graph.impactEmpty}
              markerColor={GRAPH_NODE_MARKER_COLORS.impact}
            />
            {isBusinessServiceRoot ? (
              <AnalysisList
                title={t.graph.componentsPanel}
                items={components.map((c) => ({ id: c.id, name: c.name, hint: c.type ?? undefined }))}
                empty={t.graph.componentsEmpty}
                markerColor={GRAPH_NODE_MARKER_COLORS.components}
              />
            ) : null}
          </div>
        ) : null}

        <div className="flex flex-col gap-2">
          <Button variant="secondary" className="w-full justify-start text-xs" onClick={onFit}>
            <Maximize2 className="h-3.5 w-3.5" /> {t.graph.fitView}
          </Button>
          <Button variant="secondary" className="w-full justify-start text-xs" onClick={onRelayout}>
            <RotateCcw className="h-3.5 w-3.5" /> {t.graph.resetLayout}
          </Button>
          {canExport ? (
            <Button variant="secondary" className="w-full justify-start text-xs" onClick={onExport}>
              <Image className="h-3.5 w-3.5" /> PNG
            </Button>
          ) : null}
          <Button
            variant="secondary"
            className="w-full justify-start text-xs"
            onClick={onValidate}
            disabled={validating}
            data-testid="graph-validate"
          >
            <ShieldCheck className="h-3.5 w-3.5" /> {t.graph.validate}
          </Button>
          {canEdit && onAutodiscover && hasRoot ? (
            <Button
              variant="secondary"
              className="w-full justify-start text-xs"
              onClick={onAutodiscover}
              data-testid="graph-autodiscover"
            >
              <Radar className="h-3.5 w-3.5" /> {t.autodiscover.title}
            </Button>
          ) : null}
        </div>

        {validation ? (
          <RelationValidationBanner
            validation={validation}
            validLabel={t.graph.validationOk}
            issuesLabel={t.graph.validationIssues}
          />
        ) : null}

        {nodeCount > 0 ? (
          <p className="text-xs text-[var(--text-primary)]">
            {t.graph.nodesCount}: {nodeCount} · {t.graph.edgesCount}: {edgeCount}
          </p>
        ) : null}
      </div>

      <div className="text-caption shrink-0 space-y-1 border-t border-[var(--border-subtle)] p-4 leading-relaxed text-[var(--text-muted)]">
        <p>{t.graph.hint}</p>
        <p>{t.graph.positionsHint}</p>
      </div>
    </aside>
  )
}
