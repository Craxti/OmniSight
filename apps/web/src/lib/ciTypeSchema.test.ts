import { describe, expect, it } from 'vitest'
import {
  buildSchemaJson,
  countSchemaFields,
  hasDuplicateSchemaKeys,
  listSchemaFieldKeys,
  parseSchemaFields,
} from '@/lib/ciTypeSchema'

describe('ciTypeSchema', () => {
  it('round-trips fields through JSON', () => {
    const json = buildSchemaJson([
      { key: 'port', type: 'integer', description: 'TCP port' },
      { key: 'engine', type: 'string', description: '' },
    ])
    const { fields, error } = parseSchemaFields(json)
    expect(error).toBeUndefined()
    expect(fields).toEqual([
      { key: 'port', type: 'integer', description: 'TCP port' },
      { key: 'engine', type: 'string', description: '' },
    ])
  })

  it('reports invalid JSON', () => {
    const result = parseSchemaFields('{ broken')
    expect(result.error).toBe('invalid_json')
  })

  it('counts and lists schema keys', () => {
    const schema = { properties: { a: { type: 'string' }, b: { type: 'integer' } } }
    expect(countSchemaFields(schema)).toBe(2)
    expect(listSchemaFieldKeys(schema)).toEqual(['a', 'b'])
  })

  it('detects duplicate keys', () => {
    expect(hasDuplicateSchemaKeys([{ key: 'x', type: 'string', description: '' }, { key: 'x', type: 'integer', description: '' }])).toBe(true)
    expect(hasDuplicateSchemaKeys([{ key: 'x', type: 'string', description: '' }, { key: 'y', type: 'string', description: '' }])).toBe(false)
  })
})
