import type { messages } from '@/i18n/messages'

type AuditMessages = (typeof messages)['en']['audit']

export function auditActionLabel(t: AuditMessages, action: string): string {
  const labels: Record<string, string> = {
    create: t.actionCreate,
    update: t.actionUpdate,
    delete: t.actionDelete,
    purge: t.actionPurge,
    restore: t.actionRestore,
    export_full: t.actionExportFull,
    import_create: t.actionImportCreate,
    import_update: t.actionImportUpdate,
    import_ci_json: t.actionImportCiJson,
    import_relations_json: t.actionImportRelationsJson,
    import_relations_csv: t.actionImportRelationsCsv,
  }
  return labels[action] ?? action
}

export function auditEntityTypeLabel(t: AuditMessages, entityType: string): string {
  const labels: Record<string, string> = {
    ci: t.entityCi,
    relation: t.entityRelation,
    import: t.entityImport,
    export: t.entityExport,
    ci_type: t.entityCiType,
  }
  return labels[entityType] ?? entityType
}
