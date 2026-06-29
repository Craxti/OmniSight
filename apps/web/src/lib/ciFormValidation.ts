/**
 * IP validation aligned with API `src/core/ip_validation.py` (stdlib ipaddress semantics).
 * Contract vectors: fixtures/ip-validation-vectors.json
 */

/** Validates IPv4 or IPv6 literal (format only, no reachability check). */
export function isValidIpAddress(value: string): boolean {
  const v = value.trim()
  if (!v) return true

  let text = v
  if (text.startsWith('[') && text.endsWith(']')) {
    text = text.slice(1, -1)
  }

  if (isValidIpv4(text)) return true
  return isValidIpv6(text)
}

function isValidIpv4(ip: string): boolean {
  const parts = ip.split('.')
  if (parts.length !== 4) return false
  return parts.every((part) => {
    if (!/^\d{1,3}$/.test(part)) return false
    const n = Number(part)
    return n >= 0 && n <= 255 && String(n) === String(Number(part))
  })
}

function isValidIpv6(ip: string): boolean {
  const lower = ip.toLowerCase()
  if (!lower.includes(':')) return false
  if (!/^[0-9a-f:]+$/.test(lower)) return false

  const [head, tail] = lower.split('::')
  const headGroups = head ? head.split(':').filter(Boolean) : []
  const tailGroups = tail !== undefined ? tail.split(':').filter(Boolean) : []

  if (tail === undefined) {
    if (headGroups.length !== 8) return false
    return headGroups.every(isValidIpv6Group)
  }

  if (lower.split('::').length > 2) return false
  const total = headGroups.length + tailGroups.length
  if (total >= 8) return false
  return [...headGroups, ...tailGroups].every(isValidIpv6Group)
}

function isValidIpv6Group(group: string): boolean {
  return group.length > 0 && group.length <= 4 && /^[0-9a-f]+$/.test(group)
}
