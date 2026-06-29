import { Modal } from '@/components/ui'
import { FormField } from '@/shared/components/FormField'
import { FormModalActions } from '@/shared/components/FormModalActions'
import { useI18n } from '@/context/useI18n'
import type { SyncConnector, SyncConnectorInput } from '@/shared/api/autodiscover'
import { useConnectorForm } from '@/features/settings/hooks/useConnectorForm'
import type { ConnectorFormState, HostSshAuth, ServerCiMode } from '@/features/settings/connectorFormState'

export type { ConnectorFormState, HostSshAuth }

type Props = {
  open: boolean
  initial?: SyncConnector | null
  onClose: () => void
  onSubmit: (body: SyncConnectorInput, form: ConnectorFormState) => void
  pending?: boolean
}

export function ConnectorFormModal({ open, initial, onClose, onSubmit, pending }: Props) {
  const { t } = useI18n()
  const { form, setForm, isHost, serverItems, saveBlockedReason, submit, errors } = useConnectorForm(open, initial, onSubmit)

  return (
    <Modal open={open} onClose={onClose} title={initial ? t.settings.connectors.editTitle : t.settings.connectors.newTitle} wide>
      <div className="space-y-3">
        {isHost && !initial ? (
          <p className="alert alert-info">{t.settings.connectors.hostSteps}</p>
        ) : null}

        <FormField label={t.settings.connectors.colName} htmlFor="connector-name" error={errors.name?.message}>
          <input
            id="connector-name"
            className={`input ${errors.name ? 'border-red-500/60' : ''}`}
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            data-testid="connector-name"
          />
        </FormField>

        <div className="grid gap-3 sm:grid-cols-2">
          <FormField label={t.settings.connectors.colType} htmlFor="connector-type">
            <select
              id="connector-type"
              className="input"
              value={form.connector_type}
              disabled={!!initial}
              onChange={(e) => setForm({ ...form, connector_type: e.target.value as ConnectorFormState['connector_type'] })}
              data-testid="connector-type"
            >
              {(['host', 'file', 'db', 'api', 'stream'] as const).map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </FormField>

          <FormField
            label={`${t.settings.connectors.colServer}${isHost ? ' *' : ''}`}
            htmlFor="connector-server"
            hint={
              isHost
                ? form.server_ci_mode === 'new'
                  ? t.settings.connectors.newServerHint
                  : form.server_ci_id
                    ? t.settings.connectors.hostServerHint
                    : t.settings.connectors.needServerCi
                : undefined
            }
            hintTone={isHost && form.server_ci_mode === 'existing' && !form.server_ci_id ? 'warning' : 'muted'}
          >
            {isHost && !initial ? (
              <div className="mb-2 flex flex-wrap gap-3 text-sm">
                {(['existing', 'new'] as const).map((mode) => (
                  <label key={mode} className="flex cursor-pointer items-center gap-1.5">
                    <input
                      type="radio"
                      name="connector-server-mode"
                      value={mode}
                      checked={form.server_ci_mode === mode}
                      onChange={() => setForm({ ...form, server_ci_mode: mode as ServerCiMode, server_ci_id: '' })}
                      data-testid={`connector-server-mode-${mode}`}
                    />
                    {mode === 'existing'
                      ? t.settings.connectors.serverModeExisting
                      : t.settings.connectors.serverModeNew}
                  </label>
                ))}
              </div>
            ) : null}

            {isHost && form.server_ci_mode === 'new' && !initial ? (
              <div className="space-y-3">
                <input
                  id="connector-new-server-name"
                  className={`input ${errors.new_server_name ? 'border-red-500/60' : ''}`}
                  value={form.new_server_name}
                  onChange={(e) => setForm({ ...form, new_server_name: e.target.value })}
                  placeholder={t.settings.connectors.newServerName}
                  data-testid="connector-new-server-name"
                />
                <div className="grid gap-3 sm:grid-cols-2">
                  <input
                    id="connector-new-server-hostname"
                    className={`input font-mono text-xs ${errors.new_server_hostname ? 'border-red-500/60' : ''}`}
                    value={form.new_server_hostname}
                    onChange={(e) => setForm({ ...form, new_server_hostname: e.target.value })}
                    placeholder={t.settings.connectors.newServerHostname}
                    data-testid="connector-new-server-hostname"
                  />
                  <input
                    id="connector-new-server-ip"
                    className={`input font-mono text-xs ${errors.new_server_ip ? 'border-red-500/60' : ''}`}
                    value={form.new_server_ip}
                    onChange={(e) => setForm({ ...form, new_server_ip: e.target.value })}
                    placeholder={t.settings.connectors.newServerIp}
                    data-testid="connector-new-server-ip"
                  />
                </div>
                {errors.new_server_name?.message ? (
                  <p className="text-xs text-red-400">{errors.new_server_name.message}</p>
                ) : null}
                {errors.new_server_hostname?.message ? (
                  <p className="text-xs text-red-400">{errors.new_server_hostname.message}</p>
                ) : null}
                {errors.new_server_ip?.message ? (
                  <p className="text-xs text-red-400">{errors.new_server_ip.message}</p>
                ) : null}
              </div>
            ) : (
              <select
                id="connector-server"
                className={`input ${isHost && form.server_ci_mode === 'existing' && !form.server_ci_id ? 'ring-1 ring-amber-400/80' : ''}`}
                value={form.server_ci_id}
                onChange={(e) => setForm({ ...form, server_ci_id: e.target.value })}
                data-testid="connector-server"
              >
                <option value="">{t.common.selectPlaceholder}</option>
                {serverItems.map((srv) => (
                  <option key={srv.id} value={srv.id}>{srv.name}</option>
                ))}
              </select>
            )}
          </FormField>
        </div>

        {isHost ? (
          <>
            <div className="grid gap-3 sm:grid-cols-2">
              <FormField label={t.settings.connectors.sshHost} htmlFor="connector-ssh-host">
                <input
                  id="connector-ssh-host"
                  className="input font-mono text-xs"
                  value={form.ssh_host}
                  onChange={(e) => setForm({ ...form, ssh_host: e.target.value })}
                  placeholder={t.settings.connectors.sshHostPlaceholder}
                  data-testid="connector-ssh-host"
                />
              </FormField>
              <FormField label={t.settings.connectors.sshPort} htmlFor="connector-ssh-port">
                <input
                  id="connector-ssh-port"
                  className="input font-mono text-xs"
                  value={form.ssh_port}
                  onChange={(e) => setForm({ ...form, ssh_port: e.target.value })}
                  placeholder="22"
                  data-testid="connector-ssh-port"
                />
              </FormField>
            </div>
            <FormField label={t.settings.connectors.sshUser} htmlFor="connector-ssh-user">
              <input
                id="connector-ssh-user"
                className="input font-mono text-xs"
                value={form.ssh_user}
                onChange={(e) => setForm({ ...form, ssh_user: e.target.value })}
                placeholder="root"
                data-testid="connector-ssh-user"
              />
            </FormField>
            <FormField label={t.settings.connectors.sshAuth} htmlFor="connector-ssh-auth">
              <select
                id="connector-ssh-auth"
                className="input"
                value={form.ssh_auth}
                onChange={(e) => setForm({ ...form, ssh_auth: e.target.value as HostSshAuth })}
                data-testid="connector-ssh-auth"
              >
                <option value="password">{t.settings.connectors.sshAuthPassword}</option>
                <option value="key">{t.settings.connectors.sshAuthKey}</option>
                <option value="agent">{t.settings.connectors.sshAuthAgent}</option>
              </select>
            </FormField>
            {form.ssh_auth === 'password' ? (
              <FormField label={t.settings.connectors.sshPassword} htmlFor="connector-ssh-password">
                <input
                  id="connector-ssh-password"
                  type="password"
                  className="input font-mono text-xs"
                  value={form.ssh_password}
                  onChange={(e) => setForm({ ...form, ssh_password: e.target.value })}
                  autoComplete="new-password"
                  data-testid="connector-ssh-password"
                />
              </FormField>
            ) : null}
            {form.ssh_auth === 'key' ? (
              <FormField label={t.settings.connectors.sshKeyPath} htmlFor="connector-ssh-key">
                <input
                  id="connector-ssh-key"
                  className="input font-mono text-xs"
                  value={form.ssh_key_path}
                  onChange={(e) => setForm({ ...form, ssh_key_path: e.target.value })}
                  placeholder="C:\Users\you\.ssh\id_rsa"
                  data-testid="connector-ssh-key"
                />
              </FormField>
            ) : null}
            <FormField label={t.settings.connectors.hostSnapshotPath} htmlFor="connector-path" hint={t.settings.connectors.hostHint}>
              <input
                id="connector-path"
                className="input font-mono text-xs"
                value={form.path}
                onChange={(e) => setForm({ ...form, path: e.target.value })}
                placeholder={t.settings.connectors.hostSnapshotOptional}
                data-testid="connector-path"
              />
            </FormField>
          </>
        ) : null}

        {form.connector_type === 'file' && (
          <FormField label={t.settings.connectors.filePath} htmlFor="connector-file-path">
            <input
              id="connector-file-path"
              className="input font-mono text-xs"
              value={form.path}
              onChange={(e) => setForm({ ...form, path: e.target.value })}
              placeholder="D:\data\inventory.json"
              data-testid="connector-path"
            />
          </FormField>
        )}
        {form.connector_type === 'api' && (
          <FormField label="URL" htmlFor="connector-url">
            <input
              id="connector-url"
              className="input font-mono text-xs"
              value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder="http://127.0.0.1:8000/api/v1/..."
            />
          </FormField>
        )}
        {form.connector_type === 'db' && (
          <>
            <FormField label="SQL" htmlFor="connector-query">
              <textarea
                id="connector-query"
                className="input min-h-[100px] font-mono text-xs"
                value={form.query}
                onChange={(e) => setForm({ ...form, query: e.target.value })}
              />
            </FormField>
            <FormField label={t.settings.connectors.dbUrlEnv} htmlFor="connector-db-url-env">
              <input
                id="connector-db-url-env"
                className="input font-mono text-xs"
                value={form.database_url_env}
                onChange={(e) => setForm({ ...form, database_url_env: e.target.value })}
              />
            </FormField>
          </>
        )}

        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} />
          {t.settings.connectors.colEnabled}
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={form.auto_sync}
            onChange={(e) => setForm({ ...form, auto_sync: e.target.checked })}
            data-testid="connector-auto-sync"
          />
          {t.settings.connectors.autoSync}
        </label>
        <p className="hint">{t.settings.connectors.autoSyncHint}</p>
      </div>
      <FormModalActions
        layout="split"
        footerNote={saveBlockedReason}
        onCancel={onClose}
        onSubmit={submit}
        submitLabel={t.common.save}
        pending={pending}
        submitDisabled={!!saveBlockedReason}
        submitTestId="connector-save"
      />
    </Modal>
  )
}
