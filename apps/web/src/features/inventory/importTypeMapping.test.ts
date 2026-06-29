import { describe, expect, it } from 'vitest'
import { buildMappingEntries, initialMappingRow } from '@/features/inventory/importTypeMapping'

describe('importTypeMapping', () => {
  it('initializes unknown types as create-new drafts', () => {
    const row = initialMappingRow({
      source_type: 'Edge Gateway',
      item_count: 2,
      status: 'unknown',
      draft: {
        name: 'Edge Gateway',
        description: 'draft',
        attribute_schema: { properties: { region: { type: 'string' } } },
      },
    })
    expect(row.createNew).toBe(true)
    expect(row.expanded).toBe(true)
    expect(row.draftName).toBe('Edge Gateway')
  })

  it('builds create_new mapping entries from rows', () => {
    const entries = buildMappingEntries([
      {
        source_type: 'Stream Processor',
        item_count: 1,
        status: 'unknown',
        action: 'create_new',
        target_type_id: null,
        createNew: true,
        draftName: 'Stream Processor',
        draftDescription: 'e2e',
        draftSchemaJson: '{"properties":{"topic":{"type":"string"}}}',
        expanded: true,
      },
    ])
    expect(entries).toEqual([
      {
        source_type: 'Stream Processor',
        action: 'create_new',
        draft: {
          name: 'Stream Processor',
          description: 'e2e',
          attribute_schema: { properties: { topic: { type: 'string' } } },
        },
      },
    ])
  })

  it('skips matched types in mapping payload', () => {
    const entries = buildMappingEntries([
      {
        source_type: 'Server',
        item_count: 1,
        status: 'matched',
        action: 'use_existing',
        target_type_id: 5,
        createNew: false,
        draftName: 'Server',
        draftDescription: '',
        draftSchemaJson: '{}',
        expanded: false,
      },
    ])
    expect(entries).toEqual([])
  })
})
