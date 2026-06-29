import { KeyRound, Plus, Trash2, UserCheck, UserX, Users } from 'lucide-react'
import { useMemo } from 'react'
import type { UserInfo } from '@/shared/api'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'
import { SectionHead } from '@/features/settings/components/SettingsUi'

type Props = {
  users: UserInfo[] | undefined
  currentUserEmail: string | undefined
  onAddUser: () => void
  onResetPassword: (email: string) => void
  onToggleActive: (email: string, is_active: boolean) => void
  onDeleteUser: (email: string) => void
  onRoleChange: (email: string, role: string) => void
}

export function UsersTab({
  users,
  currentUserEmail,
  onAddUser,
  onResetPassword,
  onToggleActive,
  onDeleteUser,
  onRoleChange,
}: Props) {
  const { t } = useI18n()
  const rows = users ?? []

  const columns = useMemo((): VirtualColumn<UserInfo>[] => [
    {
      id: 'email',
      header: 'Email',
      width: 'minmax(180px, 1.5fr)',
      cell: (u) => {
        const isSelf = u.email === currentUserEmail
        return (
          <span className={`inline-flex flex-wrap items-center gap-2 font-medium ${!u.is_active ? 'opacity-60' : ''}`}>
            <span>{u.email}</span>
            {isSelf && <span className="badge badge-indigo">{t.settings.youLabel}</span>}
          </span>
        )
      },
    },
    {
      id: 'role',
      header: t.settings.colRole,
      width: 'minmax(120px, 1fr)',
      cell: (u) => {
        const isSelf = u.email === currentUserEmail
        return (
          <select
            className="input max-w-[8rem] py-1.5 text-xs"
            value={u.role}
            disabled={isSelf}
            onChange={(e) => onRoleChange(u.email, e.target.value)}
          >
            <option value="viewer">{t.settings.roles.viewer}</option>
            <option value="editor">{t.settings.roles.editor}</option>
            <option value="admin">{t.settings.roles.admin}</option>
          </select>
        )
      },
    },
    {
      id: 'active',
      header: t.settings.colActive,
      width: 'minmax(100px, 0.8fr)',
      hideMobile: true,
      cell: (u) => (
        <span className={`badge ${u.is_active ? 'badge-green' : 'badge-gray'}`}>
          {u.is_active ? t.settings.active : t.settings.inactive}
        </span>
      ),
    },
    {
      id: 'actions',
      header: t.settings.colActions,
      width: 'minmax(220px, 1.4fr)',
      cellClassName: 'virtual-table-td-actions',
      cell: (u) => {
        const isSelf = u.email === currentUserEmail
        return (
          <div className="flex flex-wrap items-center gap-1.5">
            <Button variant="table-primary" onClick={() => onResetPassword(u.email)} disabled={!u.is_active}>
              <KeyRound className="h-3.5 w-3.5" />
              {t.settings.resetPassword}
            </Button>
            {!isSelf && (
              <Button variant="table-warn" onClick={() => onToggleActive(u.email, !u.is_active)}>
                {u.is_active ? <UserX className="h-3.5 w-3.5" /> : <UserCheck className="h-3.5 w-3.5" />}
                {u.is_active ? t.settings.deactivate : t.settings.activate}
              </Button>
            )}
            {!isSelf && (
              <Button variant="table-danger" onClick={() => onDeleteUser(u.email)}>
                <Trash2 className="h-3.5 w-3.5" />
                {t.settings.deleteUser}
              </Button>
            )}
          </div>
        )
      },
    },
  ], [currentUserEmail, onDeleteUser, onResetPassword, onRoleChange, onToggleActive, t])

  return (
    <>
      <SectionHead
        icon={Users}
        title={t.settings.users}
        tone="success"
        action={(
          <Button variant="primary" onClick={onAddUser}>
            <Plus className="h-4 w-4" /> {t.settings.addUser}
          </Button>
        )}
      />
      <VirtualDataTable
        items={rows}
        columns={columns}
        getRowKey={(u) => u.email}
        ariaLabel={t.settings.users}
        testId="users-table"
        maxHeight="min(60vh, 640px)"
      />
    </>
  )
}
