import { describe, expect, it } from 'vitest'
import { getChangedAuditKeys, truncateAuditValue } from '@/features/audit/auditDiff'

describe('auditDiff', () => {
  it('limits purge snapshots to priority fields', () => {
    const oldValue = {
      id: 1,
      name: 'demo-hub-srv',
      status: 'archived',
      type_name: 'Server',
      owner: 'ops',
      attributes: { ip: '10.0.0.1' },
    }

    expect(getChangedAuditKeys(oldValue, null)).toEqual(['name', 'type_name', 'status', 'owner'])
  })

  it('keeps real field diffs for updates', () => {
    const oldValue = { name: 'a', status: 'active', owner: 'ops' }
    const newValue = { name: 'a', status: 'archived', owner: 'ops' }

    expect(getChangedAuditKeys(oldValue, newValue)).toEqual(['status'])
  })

  it('truncates long values', () => {
    expect(truncateAuditValue('x'.repeat(50), 10)).toBe('xxxxxxxxx…')
  })
})
