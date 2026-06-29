import type { AutodiscoverFieldMapping } from '@/shared/api/autodiscover'
import type { useI18n } from '@/context/useI18n'

type Messages = ReturnType<typeof useI18n>['t']

export function kindLabel(kind: AutodiscoverFieldMapping['mapping_kind'], t: Messages) {
  if (kind === 'relation') return t.autodiscover.kindRelation
  if (kind === 'ci_create') return t.autodiscover.kindCiCreate
  return t.autodiscover.kindField
}

export function confidenceLabel(confidence: number, t: Messages) {
  const pct = Math.round(confidence * 100)
  if (confidence >= 0.85) return `${pct}% · ${t.autodiscover.statusAuto}`
  if (confidence >= 0.5) return `${pct}% · ${t.autodiscover.statusReview}`
  return `${pct}% · ${t.autodiscover.statusConflict}`
}

export function AutodiscoverStatusBadge({
  status,
  t,
}: {
  status: AutodiscoverFieldMapping['status']
  t: Messages
}) {
  if (status === 'auto' || status === 'applied') {
    return <span className="badge badge-green">{t.autodiscover.statusAuto}</span>
  }
  if (status === 'conflict') {
    return <span className="badge badge-red">{t.autodiscover.statusConflict}</span>
  }
  return <span className="badge badge-amber">{t.autodiscover.statusReview}</span>
}
