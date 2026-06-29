import { createContext } from 'react'
import { messages, type Locale } from '@/i18n/messages'

export interface I18nContextValue {
  locale: Locale
  setLocale: (l: Locale) => void
  t: (typeof messages)[Locale]
  dateLocale: string
}

export const I18nContext = createContext<I18nContextValue | null>(null)
