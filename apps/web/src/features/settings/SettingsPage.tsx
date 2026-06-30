import { PageHeader } from '@/components/ui'
import { fmt } from '@/i18n/messages'
import { ConfirmDialog } from '@/shared/components/ConfirmDialog'
import { TabBar } from '@/shared/components/TabBar'
import { ApiTab } from '@/features/settings/components/ApiTab'
import { CiTypeFormModal } from '@/features/settings/components/CiTypeFormModal'
import { CiTypesTab } from '@/features/settings/components/CiTypesTab'
import { ConnectorFormModal } from '@/features/settings/components/ConnectorFormModal'
import { ConnectorsTab } from '@/features/settings/components/ConnectorsTab'
import { PasswordResetModal } from '@/features/settings/components/PasswordResetModal'
import { UserCreateModal } from '@/features/settings/components/UserCreateModal'
import { UsersTab } from '@/features/settings/components/UsersTab'
import { RelationTypeFormModal } from '@/features/settings/components/RelationTypeFormModal'
import { RelationTypesSection } from '@/features/settings/components/RelationTypesSection'
import { useSettingsPage } from '@/features/settings/hooks/useSettingsPage'

export default function SettingsPage() {
  const s = useSettingsPage()

  return (
    <div className="space-y-6">
      <PageHeader title={s.t.settings.title} subtitle={s.t.settings.subtitle} />

      <TabBar
        ariaLabel={s.t.settings.title}
        items={s.tabs}
        active={s.tab}
        onChange={s.setTab}
      />

      <div className="card min-w-0 overflow-hidden p-5" role="tabpanel">
        {s.tab === 'types' && (
          <>
            <CiTypesTab
              isAdmin={s.isAdmin}
              onNewType={s.openNewType}
              onEditType={s.openEditType}
              onDeleteType={(id) => s.deleteTypeMut.mutate(id)}
            />
            <RelationTypesSection
              isAdmin={s.isAdmin}
              onNewType={s.openNewRelationType}
              onEditType={s.openEditRelationType}
              onDeleteType={(id) => s.deleteRelationTypeMut.mutate(id)}
            />
          </>
        )}
        {s.tab === 'connectors' && s.canEdit && (
          <ConnectorsTab
            canEdit={s.canEdit}
            onNew={() => s.setConnectorForm(null)}
            onEdit={(c) => s.setConnectorForm(c)}
            onDelete={(c) => s.setDeleteConnector(c)}
            onTest={(c) => s.testMut.mutate(c.id)}
            onSync={(c) => s.syncMut.mutate(c.id)}
          />
        )}
        {s.tab === 'api' && <ApiTab />}
        {s.tab === 'users' && s.isAdmin && (
          <UsersTab
            users={s.users}
            currentUserEmail={s.currentUser?.email}
            onAddUser={s.openCreateUser}
            onResetPassword={s.openResetPassword}
            onToggleActive={(email, is_active) => s.activeMut.mutate({ email, is_active })}
            onDeleteUser={s.setDeleteFor}
            onRoleChange={(email, role) => s.roleMut.mutate({ email, role })}
          />
        )}
      </div>

      <ConnectorFormModal
        open={s.connectorForm !== undefined}
        initial={s.connectorForm}
        onClose={() => s.setConnectorForm(undefined)}
        pending={s.submittingConnector || s.createConnectorMut.isPending || s.updateConnectorMut.isPending}
        onSubmit={s.submitConnector}
      />

      <ConfirmDialog
        open={!!s.deleteConnector}
        title={s.t.settings.connectors.deleteTitle}
        message={s.deleteConnector?.name}
        confirmLabel={s.t.settings.connectors.deleteConfirm}
        onClose={() => s.setDeleteConnector(null)}
        onConfirm={() =>
          s.deleteConnectorMut.mutate(s.deleteConnector!.id, { onSuccess: () => s.setDeleteConnector(null) })
        }
        pending={s.deleteConnectorMut.isPending}
      />

      <ConfirmDialog
        open={!!s.deleteFor}
        title={s.t.settings.deleteUserTitle}
        message={s.deleteFor ? fmt(s.t.settings.deleteUserConfirm, { email: s.deleteFor }) : null}
        confirmLabel={s.t.settings.deleteUser}
        onClose={() => s.setDeleteFor(null)}
        onConfirm={() => s.deleteUserMut.mutate(s.deleteFor!, { onSuccess: () => s.setDeleteFor(null) })}
        pending={s.deleteUserMut.isPending}
      />

      <UserCreateModal
        open={s.createUserOpen}
        pending={s.createUserMut.isPending}
        onClose={() => s.setCreateUserOpen(false)}
        onSubmit={s.submitCreateUser}
      />

      <PasswordResetModal
        open={!!s.resetEmail}
        email={s.resetEmail ?? ''}
        pending={s.resetMut.isPending}
        onClose={() => s.setResetEmail(null)}
        onSubmit={s.submitResetPassword}
      />

      <CiTypeFormModal
        open={s.typeFormOpen}
        initial={s.typeFormInitial}
        pending={s.saveTypeMut.isPending}
        onClose={s.closeTypeForm}
        onSubmit={s.saveType}
      />

      <RelationTypeFormModal
        open={s.relationTypeFormOpen}
        initial={s.relationTypeFormInitial}
        pending={s.saveRelationTypeMut.isPending}
        onClose={s.closeRelationTypeForm}
        onSubmit={s.saveRelationType}
      />
    </div>
  )
}
