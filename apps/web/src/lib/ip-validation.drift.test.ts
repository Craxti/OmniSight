/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { isValidIpAddress } from '@/lib/ciFormValidation'

const TEST_DIR = dirname(fileURLToPath(import.meta.url))

const VECTORS = JSON.parse(
  readFileSync(resolve(TEST_DIR, '../../../../fixtures/ip-validation-vectors.json'), 'utf-8'),
) as { valid: string[]; invalid: string[] }

describe('ip validation drift (web vs fixtures/ip-validation-vectors.json)', () => {
  it.each(VECTORS.valid)('accepts %j', (value) => {
    expect(isValidIpAddress(value)).toBe(true)
  })

  it.each(VECTORS.invalid)('rejects %j', (value) => {
    expect(isValidIpAddress(value)).toBe(false)
  })
})
