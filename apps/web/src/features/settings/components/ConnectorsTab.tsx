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
        width: 'minmax(140px, 1.2fr)',
        cell: (c) => <span className="font-medium">{c.name}</span>,
      },
      {
        id: 'type',
        header: t.settings.connectors.colType,
        width: 'minmax(90px, 0.8fr)',
        cell: (c) => <span className="badge badge-indigo">{c.connector_type}</span>,
      },
      {
        id: 'server',
        header: t.settings.connectors.colServer,
        width: 'minmax(80px, 0.7fr)',
        hideMobile: true,
        cell: (c) => (c.server_ci_id ? `#${c.server_ci_id}` : '—'),
      },
      {
        id: 'config',
        header: t.settings.connectors.colConfig,
        width: 'minmax(160px, 1.5fr)',
        hideMobile: true,
        cell: (c) => (
          <span className="max-w-xs truncate font-mono text-xs text-[var(--text-muted)]">
            {configSummary(c)}
            {c.has_credentials ? ` · ${t.settings.connectors.credsSet}` : ''}
          </span>
        ),
      },
      {
        id: 'enabled',
        header: t.settings.connectors.colEnabled,
        width: 'minmax(80px, 0.7fr)',
        hideMobile: true,
        cell: (c) => (c.enabled ? t.settings.active : t.settings.inactive),
      },
      {
        id: 'auto_sync',
        header: t.settings.connectors.colAutoSync,
        width: 'minmax(90px, 0.8fr)',
        hideMobile: true,
        cell: (c) => (c.auto_sync ? t.settings.connectors.autoSyncOn : '—'),
      },
    ]

    if (canEdit) {
      cols.push({
        id: 'actions',
        header: t.settings.colActions,
        width: 'minmax(180px, 1.2fr)',
        cellClassName: 'virtual-table-td-actions',
        cell: (c) => (
          <div className="flex flex-wrap gap-1.5">
            <Button
              variant="table-primary"
              iconOnly
              className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
              onClick={() => onSync(c)}
              aria-label={t.settings.connectors.syncNow}
            >
              <Radar className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table"
              iconOnly
              className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
              onClick={() => onTest(c)}
              aria-label={t.settings.connectors.test}
            >
              <Play className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table-primary"
              iconOnly
              className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
              onClick={() => onEdit(c)}
              aria-label={t.common.edit}
            >
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="table-danger"
              iconOnly
              className="min-h-11 min-w-11 md:min-h-0 md:min-w-0"
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
        <VirtualDataTable
          items={rows}
          columns={columns}
          getRowKey={(c) => c.id}
          isLoading={isLoading}
          ariaLabel={t.settings.connectors.title}
          testId="connectors-table"
          maxHeight="min(60vh, 640px)"
          virtualized={rows.length > 50}
        />
      )}
    </>
  )
}

function configSummary(c: SyncConnector): string {
  const cfg = c.config ?? {}
  if (c.connector_type === 'host') {
    const host = cfg.ssh_host ? String(cfg.ssh_host) : ''
    const snap = cfg.snapshot_path ? String(cfg.snapshot_path) : ''
    if (host && snap) return `ssh:${host} | snapshot`
    if (host) return `ssh:${host}`
    return snap || String(cfg.path ?? '')
  }
  if (c.connector_type === 'file') return String(cfg.path ?? '')
  if (c.connector_type === 'api') return String(cfg.url ?? '')
  if (c.connector_type === 'db') return String(cfg.query ?? '').slice(0, 80)
  return JSON.stringify(cfg).slice(0, 80)
}
