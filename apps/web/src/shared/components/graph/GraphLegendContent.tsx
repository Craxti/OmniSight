import { useI18n } from '@/context/useI18n'
import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { getRelationVisual, GRAPH_NODE_MARKER_COLORS, GRAPH_PATH_EDGE_COLOR } from '@/lib/graphVisuals'

type Props = {
  compact?: boolean
}

function NodeSwatch({ color }: { color: string }) {
  return (
    <span
      className="graph-legend-swatch"
      style={{ ['--swatch-color' as string]: color }}
    />
  )
}

export function GraphLegendContent({ compact = false }: Props) {
  const { t } = useI18n()
  const { relationTypes } = useDomainConstants()
  const relationLabels = t.graph.relationTypes as Record<string, string>

  const nodeMarkers = [
    { color: GRAPH_NODE_MARKER_COLORS.root, label: t.graph.origin },
    { color: GRAPH_NODE_MARKER_COLORS.impact, label: t.graph.impactZone },
    { color: GRAPH_NODE_MARKER_COLORS.components, label: t.graph.componentsZone },
  ]

  const legendText = compact ? 'text-caption' : 'text-xs'

  return (
    <div className={`select-none ${compact ? 'space-y-2' : 'space-y-5'}`}>
      <section>
        <div className={`font-medium text-[var(--text-primary)] ${compact ? 'mb-1.5 text-xs' : 'mb-2 text-sm'}`}>
          {t.graph.legendNodeMarkers}
        </div>
        <div className={`grid grid-cols-1 gap-1.5 text-[var(--text-muted)] ${legendText}`}>
          {nodeMarkers.map((item) => (
            <span key={item.label} className="flex items-center gap-2">
              <NodeSwatch color={item.color} />
              {item.label}
            </span>
          ))}
        </div>
      </section>

      <section>
        <div className={`font-medium text-[var(--text-primary)] ${compact ? 'mb-1.5 text-xs' : 'mb-2 text-sm'}`}>
          {t.graph.businessPath}
        </div>
        <div className={`flex items-center gap-2 text-[var(--text-muted)] ${legendText}`}>
          <svg width={compact ? 24 : 32} height="8" aria-hidden className="shrink-0">
            <line
              x1="0"
              y1="4"
              x2={compact ? 24 : 32}
              y2="4"
              stroke={GRAPH_PATH_EDGE_COLOR}
              strokeWidth="3"
            />
          </svg>
          <span>{t.graph.legendPathLine}</span>
        </div>
      </section>

      <section>
        <div className={`font-medium text-[var(--text-primary)] ${compact ? 'mb-1.5 text-xs' : 'mb-2 text-sm'}`}>
          {t.graph.legendRelations}
        </div>
        <div className={compact ? 'space-y-1' : 'space-y-1.5'}>
          {relationTypes.map((rt) => {
            const visual = getRelationVisual(rt)
            return (
              <div
                key={rt}
                className={`flex items-center gap-2 text-[var(--text-muted)] ${legendText}`}
              >
                <svg width={compact ? 20 : 28} height="8" aria-hidden className="shrink-0">
                  <line
                    x1="0"
                    y1="4"
                    x2={compact ? 20 : 28}
                    y2="4"
                    stroke={visual.color}
                    strokeWidth={visual.strokeWidth}
                    strokeDasharray={visual.dash}
                  />
                </svg>
                <span>{relationLabels[rt] ?? rt}</span>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
