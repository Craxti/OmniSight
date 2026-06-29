import { Handle, Position, type NodeProps } from '@xyflow/react'

import { useI18n } from '@/context/useI18n'
import { getCiTypeVisual } from '@/lib/graphVisuals'

const HANDLE_CLASS = '!border-2 graph-node-handle'
const HANDLE_EDITABLE = `${HANDLE_CLASS} !w-3 !h-3 opacity-90`
const HANDLE_READONLY = `${HANDLE_CLASS} !w-2 !h-2 opacity-0 group-hover:opacity-100`

function nodeRoleClass(
  isRoot: boolean,
  inImpact: boolean,
  inComponents: boolean,
  onPath: boolean,
  inAlert: boolean,
): string {
  if (isRoot) return 'graph-node-root'
  if (inImpact) return 'graph-node-impact'
  if (inComponents) return 'graph-node-components'
  if (inAlert) return 'graph-node-alert'
  if (onPath) return 'graph-node-path'
  return ''
}

export function ResourceNode({ data, selected }: NodeProps) {
  const { t } = useI18n()
  const onPath = Boolean(data.onPath)
  const isRoot = Boolean(data.isRoot)
  const inImpact = Boolean(data.inImpact)
  const inComponents = Boolean(data.inComponents)
  const inAlert = Boolean(data.inAlert)
  const editable = Boolean(data.editable)
  const dimmed = Boolean(data.dimmed)
  const ciType = String(data.type ?? '')
  const visual = getCiTypeVisual(ciType)
  const Icon = visual.icon
  const roleClass = nodeRoleClass(isRoot, inImpact, inComponents, onPath, inAlert)
  const rootBadge = String(data.rootBadge ?? '')
  const alertBadge = String(data.alertBadge ?? '')

  const handleSize = editable ? HANDLE_EDITABLE : HANDLE_READONLY

  return (
    <div
      className={`graph-node-card group relative flex min-w-[168px] max-w-[220px] gap-2.5 rounded-xl px-3 py-2.5 shadow-xl backdrop-blur-sm ${roleClass} ${selected ? 'graph-node-selected' : ''} ${dimmed ? 'graph-node-dimmed' : ''}`}
      style={{ opacity: dimmed ? 0.42 : 1 }}
      title={editable ? t.graph.connectHint : t.graph.dblClickHint}
    >
      <Handle type="target" position={Position.Top} id="top" className={`${handleSize}`} style={{ background: visual.accent }} />
      <Handle type="target" position={Position.Left} id="left" className={`${handleSize}`} style={{ background: visual.accent }} />

      <div
        className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
        style={{ background: visual.iconBg, color: visual.accent }}
      >
        <Icon className="h-4.5 w-4.5" strokeWidth={2} aria-hidden />
      </div>

      <div className="min-w-0 flex-1">
        <div
          className="graph-node-type text-caption truncate font-semibold uppercase tracking-wide"
          style={{ color: visual.accent }}
        >
          {ciType}
        </div>
        <div className="graph-node-title truncate text-sm font-semibold" title={data.label as string}>
          {data.label as string}
        </div>
        <div className="mt-1 flex flex-wrap gap-1">
          {isRoot ? (
            <span className="graph-node-badge graph-node-badge--origin">{rootBadge || t.graph.origin}</span>
          ) : null}
          {inAlert ? (
            <span className="graph-node-badge graph-node-badge--alert">{alertBadge || t.graph.businessPath}</span>
          ) : null}
          {onPath ? (
            <span className="graph-node-badge graph-node-badge--path">{t.graph.businessPath}</span>
          ) : null}
          {inImpact ? (
            <span className="graph-node-badge graph-node-badge--impact">{t.graph.impactZone}</span>
          ) : null}
          {inComponents ? (
            <span className="graph-node-badge graph-node-badge--components">{t.graph.componentsZone}</span>
          ) : null}
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} id="bottom" className={`${handleSize}`} style={{ background: visual.accent }} />
      <Handle type="source" position={Position.Right} id="right" className={`${handleSize}`} style={{ background: visual.accent }} />
    </div>
  )
}

export const graphNodeTypes = { resource: ResourceNode }
