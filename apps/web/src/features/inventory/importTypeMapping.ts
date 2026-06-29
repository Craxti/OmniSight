import type { ImportTypeProposal, ImportTypeMappingEntry } from '@/shared/api/types'

export type MappingRowState = {
  source_type: string
  item_count: number
  status: ImportTypeProposal['status']
  action: 'use_existing' | 'create_new' | 'skip'
  target_type_id: number | null
  createNew: boolean
  draftName: string
  draftDescription: string
  draftSchemaJson: string
  expanded: boolean
}

export function initialMappingRow(proposal: ImportTypeProposal): MappingRowState {
  const draft = proposal.draft
  const useExisting = proposal.status === 'matched' || proposal.status === 'suggested_match'
  return {
    source_type: proposal.source_type,
    item_count: proposal.item_count,
    status: proposal.status,
    action: useExisting ? 'use_existing' : 'create_new',
    target_type_id: proposal.matched_type_id ?? null,
    createNew: proposal.status === 'unknown',
    draftName: draft?.name ?? proposal.source_type,
    draftDescription: draft?.description ?? '',
    draftSchemaJson: JSON.stringify(draft?.attribute_schema ?? { properties: {} }, null, 2),
    expanded: proposal.status === 'unknown',
  }
}

export function buildMappingEntries(rows: MappingRowState[]): ImportTypeMappingEntry[] {
  return rows
    .filter((row) => row.status !== 'matched')
    .map((row) => {
      if (row.createNew) {
        let schema: Record<string, unknown> = { properties: {} }
        try {
          schema = JSON.parse(row.draftSchemaJson) as Record<string, unknown>
        } catch {
          schema = { properties: {} }
        }
        return {
          source_type: row.source_type,
          action: 'create_new' as const,
          draft: {
            name: row.draftName.trim(),
            description: row.draftDescription.trim() || undefined,
            attribute_schema: schema,
          },
        }
      }
      return {
        source_type: row.source_type,
        action: row.target_type_id ? ('use_existing' as const) : ('skip' as const),
        target_type_id: row.target_type_id,
      }
    })
}
