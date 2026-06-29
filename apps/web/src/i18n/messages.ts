import { en } from '@/i18n/locales/en'
import { ru } from '@/i18n/locales/ru'

export type Locale = 'ru' | 'en'

export const messages = { ru, en } as const

export function dateLocale(locale: Locale): string {
  return locale === 'ru' ? 'ru-RU' : 'en-US'
}

export function fmt(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ''))
}
