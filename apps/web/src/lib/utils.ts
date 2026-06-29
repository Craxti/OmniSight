import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const STATUS_COLORS: Record<string, string> = {
  active: '#10b981',
  temporarily_disabled: '#f59e0b',
  decommissioned: '#ef4444',
  archived: '#64748b',
}

export function statusBadge(status: string) {
  const map: Record<string, string> = {
    active: 'badge-green',
    temporarily_disabled: 'badge-yellow',
    decommissioned: 'badge-red',
    archived: 'badge-gray',
  }
  return map[status] || 'badge-gray'
}

export function criticalityBadge(c: string | null | undefined) {
  const map: Record<string, string> = {
    critical: 'badge-red',
    high: 'badge-red',
    medium: 'badge-yellow',
    low: 'badge-green',
  }
  return map[c || ''] || 'badge-gray'
}
