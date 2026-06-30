import { useQuery } from '@tanstack/react-query'
import { Link2, Pencil, Play, Plus, Radar, Trash2 } from 'lucide-react'
import { useMemo } from 'react'
import { EmptyState, Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { autodiscoverApi, type SyncConnector } from '@/shared/api/autodiscover'
import { queryKeys } from '@/shared/queryKeys'
import { VirtualDataTable, type VirtualColumn } from '@/shared/components/VirtualDataTable'
import { SectionHead } from '@/features/settings/components/SettingsUi'

type Props = {
  canEdit: boolean
  onNew: () => void
  onEdit: (connector: SyncConnector) => void
  onDelete: (connector: SyncConnector) => void
  onTest: (connector: SyncConnector) => void
  onSync: (connector: SyncConnector) => void
}

export function ConnectorsTab({ canEdit, onNew, onEdit, onDelete, onTest, onSync }: Props) {
  const { t } = useI18n()
  const { data: connectors, isLoading } = useQuery({
    queryKey: queryKeys.autodiscover.connectors,
    queryFn: () => autodiscoverApi.connectors(false),
  })

  const rows = connectors ?? []

  const columns = useMemo((): VirtualColumn<SyncConnector>[] => {
    const cols: VirtualColumn<SyncConnector>[] = [
      {
        id: 'name',
        header: t.settings.connectors.colName,
        width: '2fr',
        cell: (c) => <span className="truncate font-medium">{c.name}</span>,
      },
      {
        id: 'type',
        header: t.settings.connectors.colType,
        width: '0.9fr',
        cell: (c) => <span className="badge badge-indigo">{c.connector_type}</span>,
      },
      {
        id: 'server',
        header: t.settings.connectors.colServer,
        width: '0.7fr',
        hideMobile: true,
        cell: (c) => (c.server_ci_id ? `#${c.server_ci_id}` : '—'),
      },
      {
        id: 'config',
        header: t.settings.connectors.colConfig,
        width: '1.6fr',
        hideMobile: true,
        className: 'min-w-0',
        cell: (c) => (
          <span className="block truncate font-mono text-xs text-[var(--text-muted)]" title={configSummary(c, t)}>
            {configSummary(c, t)}
          </span>
        ),
      },
      {
        id: 'enabled',
        header: t.settings.connectors.colEnabled,
        width: '0.75fr',
        hideMobile: true,
        cell: (c) => (c.enabled ? t.settings.active : t.settings.inactive),
      },
      {
        id: 'auto_sync',
        header: t.settings.connectors.colAutoSync,
        width: '0.85fr',
        hideMobile: true,
        cell: (c) => (c.auto_sync ? t.settings.connectors.autoSyncOn : '—'),
      },
    ]

    if (canEdit) {
      cols.push({
        id: 'actions',
        header: t.settings.colActions,
        width: '6.75rem',
        cellClassName: 'virtual-table-td-actions',
        cell: (c) => (
          <div className="flex shrink-0 gap-1">
            <Button
              variant="table-primary"
              iconOnly
              onClick={() => onSync(c)}
              aria-label={t.settings.connectors.syncNow}
            >
              <Radar className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table"
              iconOnly
              onClick={() => onTest(c)}
              aria-label={t.settings.connectors.test}
            >
              <Play className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table-primary"
              iconOnly
              onClick={() => onEdit(c)}
              aria-label={t.common.edit}
            >
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table-danger"
              iconOnly
              onClick={() => onDelete(c)}
              aria-label={t.common.delete}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        ),
      })
    }

    return cols
  }, [canEdit, onDelete, onEdit, onSync, onTest, t])

  return (
    <>
      <SectionHead
        icon={Link2}
        title={t.settings.connectors.title}
        tone="info"
        action={canEdit && (
          <Button variant="primary" onClick={onNew} data-testid="connector-new">
            <Plus className="h-4 w-4" /> {t.settings.connectors.new}
          </Button>
        )}
      />
      <p className="mb-4 text-sm text-[var(--text-muted)]">{t.settings.connectors.subtitle}</p>
      {!isLoading && rows.length === 0 ? (
        <EmptyState title={t.settings.connectors.empty} />
      ) : (
        <div className="connectors-table-fit min-w-0 max-w-full overflow-hidden">
          <VirtualDataTable
            items={rows}
            columns={columns}
            getRowKey={(c) => c.id}
            isLoading={isLoading}
            ariaLabel={t.settings.connectors.title}
            testId="connectors-table"
            maxHeight="min(60vh, 640px)"
            virtualized={false}
            className="w-full"
          />
        </div>
      )}
    </>
  )
}

function configSummary(c: SyncConnector, t: ReturnType<typeof useI18n>['t']): string {
  const cfg = c.config ?? {}
  let summary: string
  if (c.connector_type === 'host') {
    const host = cfg.ssh_host ? String(cfg.ssh_host) : ''
    const snap = cfg.snapshot_path ? String(cfg.snapshot_path) : ''
    summary = host ? `ssh:${host}` : snap || String(cfg.path ?? '')
  } else if (c.connector_type === 'file') {
    summary = String(cfg.path ?? '')
  } else if (c.connector_type === 'api') {
    summary = String(cfg.url ?? '')
  } else if (c.connector_type === 'db') {
    summary = String(cfg.query ?? '').slice(0, 60)
  } else {
    summary = JSON.stringify(cfg).slice(0, 60)
  }
  if (c.has_credentials) summary += ` · ${t.settings.connectors.credsSet}`
  return summary
}
