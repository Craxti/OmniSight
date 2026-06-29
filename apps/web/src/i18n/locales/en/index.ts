import { nav } from '@/i18n/locales/en/nav'
import { common } from '@/i18n/locales/en/common'
import { login } from '@/i18n/locales/en/login'
import { dashboard } from '@/i18n/locales/en/dashboard'
import { inventory } from '@/i18n/locales/en/inventory'
import { relations } from '@/i18n/locales/en/relations'
import { autodiscover } from '@/i18n/locales/en/autodiscover'
import { graph } from '@/i18n/locales/en/graph'
import { correlation } from '@/i18n/locales/en/correlation'
import { audit } from '@/i18n/locales/en/audit'
import { settings } from '@/i18n/locales/en/settings'
import { changePassword } from '@/i18n/locales/en/changePassword'
import { ciDetail } from '@/i18n/locales/en/ciDetail'
import { importReport } from '@/i18n/locales/en/importReport'

export const en = {
  nav,
  common,
  login,
  dashboard,
  inventory,
  relations,
  autodiscover,
  graph,
  correlation,
  audit,
  settings,
  changePassword,
  ciDetail,
  importReport,
} as const
export type LocaleMessages = typeof en
