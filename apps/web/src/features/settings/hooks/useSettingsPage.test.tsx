import { describe, expect, it, vi } from 'vitest'
import { messages } from '@/i18n/messages'
import { renderAppHook } from '@/test/renderHookWithProviders'
import { useSettingsPage } from '@/features/settings/hooks/useSettingsPage'
import { useSettingsTabs } from '@/features/settings/hooks/useSettingsTabs'

vi.mock('@/context/useAuth', () => ({
  useAuth: () => ({
    user: { email: 'admin@test.local', role: 'admin' },
    isAdmin: true,
    canEdit: true,
  }),
}))

vi.mock('@/context/useI18n', () => ({
  useI18n: () => ({ t: messages.en }),
}))

vi.mock('@/features/settings/hooks/useUsersSettings', () => ({
  useUsersSettings: () => ({
    userFormOpen: false,
    setUserFormOpen: vi.fn(),
  }),
}))

vi.mock('@/features/settings/hooks/useCiTypesSettings', () => ({
  useCiTypesSettings: () => ({
    typeFormOpen: false,
    openNewType: vi.fn(),
    closeTypeForm: vi.fn(),
  }),
}))

vi.mock('@/features/settings/hooks/useRelationTypesSettings', () => ({
  useRelationTypesSettings: () => ({
    relationTypeFormOpen: false,
    openNewRelationType: vi.fn(),
    closeRelationTypeForm: vi.fn(),
  }),
}))

vi.mock('@/features/settings/hooks/useConnectorsSettings', () => ({
  useConnectorsSettings: () => ({
    connectorForm: undefined,
    setConnectorForm: vi.fn(),
  }),
}))

describe('useSettingsTabs', () => {
  it('includes admin-only users tab when isAdmin', () => {
    const { result } = renderAppHook(() => useSettingsTabs())
    expect(result.current.tab).toBe('types')
    expect(result.current.tabs.map((t) => t.id)).toEqual(['types', 'connectors', 'api', 'users'])
    expect(result.current.tabs.find((t) => t.id === 'users')?.show).toBe(true)
  })
})

describe('useSettingsPage', () => {
  it('composes settings tabs and permissions', () => {
    const { result } = renderAppHook(() => useSettingsPage())
    expect(result.current.isAdmin).toBe(true)
    expect(result.current.canEdit).toBe(true)
    expect(result.current.currentUser?.email).toBe('admin@test.local')
    expect(result.current.tabs).toHaveLength(4)
    expect(result.current.typeFormOpen).toBe(false)
  })
})
