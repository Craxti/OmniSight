import { useEffect, useState, type ReactNode } from 'react'
import { messages, dateLocale as getDateLocale, type Locale } from '@/i18n/messages'
import { I18nContext } from '@/context/i18n-context'

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(() => (localStorage.getItem('omnisight_locale') as Locale) || 'ru')

  const setLocale = (l: Locale) => {
    localStorage.setItem('omnisight_locale', l)
    setLocaleState(l)
    document.documentElement.lang = l
  }

  useEffect(() => {
    document.documentElement.lang = locale
  }, [locale])

  return (
    <I18nContext.Provider value={{ locale, setLocale, t: messages[locale], dateLocale: getDateLocale(locale) }}>
      {children}
    </I18nContext.Provider>
  )
}
