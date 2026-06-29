import type { LocaleMessages } from '@/i18n/locales/en'

type LabelMap = Record<string, string>

function labelFrom(map: LabelMap, key: string): string {
  return map[key] ?? key
}

export function ciStatusLabel(t: LocaleMessages, status: string): string {
  return labelFrom(t.common.ciStatus as LabelMap, status)
}

export function relationStatusLabel(t: LocaleMessages, status: string): string {
  return labelFrom(t.common.relationStatus as LabelMap, status)
}

export function criticalityLabel(t: LocaleMessages, level: string): string {
  return labelFrom(t.common.criticality as LabelMap, level)
}

export function externalIdFieldLabel(t: LocaleMessages, field: string): string {
  return labelFrom(t.common.externalIdField as LabelMap, field)
}

/** CI type names are user-defined — show as stored, without UI locale translation. */
export function ciTypeLabel(_t: LocaleMessages, typeName: string): string {
  return typeName
}

export function relationTypeLabel(t: LocaleMessages, relationType: string, customLabel?: string): string {
  if (customLabel?.trim()) return customLabel.trim()
  return labelFrom(t.graph.relationTypes as LabelMap, relationType)
}
