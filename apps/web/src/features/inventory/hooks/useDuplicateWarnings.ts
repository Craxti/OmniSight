import { useEffect, useState } from 'react'
import { fmt } from '@/i18n/messages'
import type { Locale } from '@/i18n/messages'
import { messages } from '@/i18n/messages'

type Messages = (typeof messages)[Locale]
import { isValidIpAddress } from '@/lib/ciFormValidation'
import { ciApi, resourcesApi } from '@/shared/api'
import type { CiFormState } from '@/features/inventory/inventoryForm'

export function useDuplicateWarnings(showForm: boolean, form: CiFormState, t: Messages) {
  const [dupWarnings, setDupWarnings] = useState<{ name?: string; hostname?: string; ip?: string }>({})

  const ipValue = form.attributes.ip?.trim() || ''
  const ipFormatError = ipValue && !isValidIpAddress(ipValue) ? t.inventory.errInvalidIp : null

  useEffect(() => {
    if (!showForm) {
      setDupWarnings({})
      return
    }
    const name = form.name.trim()
    const hostname = form.attributes.hostname?.trim()
    const ip = form.attributes.ip?.trim()
    if (!name && !hostname && !ip) {
      setDupWarnings({})
      return
    }

    let cancelled = false
    const timer = setTimeout(async () => {
      const next: { name?: string; hostname?: string; ip?: string } = {}
      try {
        if (name) {
          const r = await ciApi.list({ name, limit: 1 })
          const hit = r.items?.find((c) => c.name === name)
          if (hit) {
            next.name = fmt(t.inventory.dupName, { value: name, id: hit.id })
          }
        }
        if (hostname) {
          const r = await resourcesApi.search({ hostname })
          const hit = r.items?.[0]
          if (hit) {
            next.hostname = fmt(t.inventory.dupHostname, { value: hostname, name: hit.name, id: hit.id })
          }
        }
        if (ip && isValidIpAddress(ip)) {
          const r = await resourcesApi.search({ ip })
          const hit = r.items?.[0]
          if (hit) {
            next.ip = fmt(t.inventory.dupIp, { value: ip, name: hit.name, id: hit.id })
          }
        }
      } catch {
        /* ignore lookup errors */
      }
      if (!cancelled) setDupWarnings(next)
    }, 400)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [showForm, form.name, form.attributes.hostname, form.attributes.ip, t])

  const getExternalHint = (field: 'hostname' | 'ip') => {
    if (field === 'hostname') return dupWarnings.hostname
    return dupWarnings.ip || ipFormatError || undefined
  }

  return { dupWarnings, ipFormatError, getExternalHint }
}
