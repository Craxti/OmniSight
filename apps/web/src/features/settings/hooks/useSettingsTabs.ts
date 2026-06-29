import { Boxes, Link2, Plug, Users } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'

export type SettingsTab = 'types' | 'connectors' | 'api' | 'users'

export function useSettingsTabs() {
  const { isAdmin, canEdit } = useAuth()
  const { t } = useI18n()
  const [tab, setTab] = useState<SettingsTab>('types')

  const tabs: { id: SettingsTab; label: string; icon: typeof Boxes; show?: boolean }[] = [
    { id: 'types', label: t.settings.tabTypes, icon: Boxes },
    { id: 'connectors', label: t.settings.tabConnectors, icon: Link2, show: canEdit },
    { id: 'api', label: t.settings.tabApi, icon: Plug },
    { id: 'users', label: t.settings.tabUsers, icon: Users, show: isAdmin },
  ]

  return { tab, setTab, tabs }
}
