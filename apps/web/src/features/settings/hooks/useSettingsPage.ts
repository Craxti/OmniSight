import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { useCiTypesSettings } from '@/features/settings/hooks/useCiTypesSettings'
import { useConnectorsSettings } from '@/features/settings/hooks/useConnectorsSettings'
import { useSettingsTabs } from '@/features/settings/hooks/useSettingsTabs'
import { useRelationTypesSettings } from '@/features/settings/hooks/useRelationTypesSettings'
import { useUsersSettings } from '@/features/settings/hooks/useUsersSettings'

export type { SettingsTab } from '@/features/settings/hooks/useSettingsTabs'
export type { TypeFormState } from '@/features/settings/hooks/useCiTypesSettings'

export function useSettingsPage() {
  const { user: currentUser, isAdmin, canEdit } = useAuth()
  const { t } = useI18n()
  const { tab, setTab, tabs } = useSettingsTabs()
  const usersSettings = useUsersSettings(t)
  const ciTypesSettings = useCiTypesSettings(t)
  const relationTypesSettings = useRelationTypesSettings(t)
  const connectorsSettings = useConnectorsSettings()

  return {
    t,
    currentUser,
    isAdmin,
    canEdit,
    tab,
    setTab,
    tabs,
    ...usersSettings,
    ...ciTypesSettings,
    ...relationTypesSettings,
    ...connectorsSettings,
  }
}
