import { describe, expect, it } from 'vitest'
import { auditActionLabel, auditEntityTypeLabel } from '@/features/audit/auditLabels'
import { messages } from '@/i18n/messages'

describe('auditLabels', () => {
  it('maps purge and restore actions', () => {
    const t = messages.ru.audit
    expect(auditActionLabel(t, 'purge')).toBe('Безвозвратное удаление')
    expect(auditActionLabel(t, 'restore')).toBe('Восстановление')
    expect(auditActionLabel(t, 'unknown_action')).toBe('unknown_action')
  })

  it('maps import actions', () => {
    const t = messages.ru.audit
    expect(auditActionLabel(t, 'import_create')).toBe('Создание при импорте')
    expect(auditActionLabel(t, 'import_ci_json')).toBe('Импорт CI (JSON)')
    expect(auditActionLabel(t, 'import_relations_json')).toBe('Импорт связей (JSON)')
  })

  it('maps entity types', () => {
    const t = messages.en.audit
    expect(auditEntityTypeLabel(t, 'ci')).toBe('CI')
    expect(auditEntityTypeLabel(t, 'relation')).toBe('Relations')
  })
})
