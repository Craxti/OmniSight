import { describe, expect, it } from 'vitest'
import { isValidIpAddress } from '@/lib/ciFormValidation'

describe('isValidIpAddress', () => {
  it('accepts empty value', () => {
    expect(isValidIpAddress('')).toBe(true)
    expect(isValidIpAddress('   ')).toBe(true)
  })

  it('accepts valid IPv4', () => {
    expect(isValidIpAddress('10.0.0.1')).toBe(true)
    expect(isValidIpAddress('192.168.1.255')).toBe(true)
  })

  it('accepts valid IPv6', () => {
    expect(isValidIpAddress('::1')).toBe(true)
    expect(isValidIpAddress('[::1]')).toBe(true)
  })

  it('rejects invalid IPv4', () => {
    expect(isValidIpAddress('999.0.0.1')).toBe(false)
    expect(isValidIpAddress('10.0.0')).toBe(false)
  })
})
