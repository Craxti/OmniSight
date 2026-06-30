import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ConnectorsTab } from '@/features/settings/components/ConnectorsTab'
import { renderWithProviders } from '@/test/renderWithProviders'

vi.mock('@tanstack/react-query', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@tanstack/react-query')>()
  let data: unknown[] = [
    {
      id: 1,
      name: 'demo-host',
      connector_type: 'host',
      server_ci_id: 5,
      config: { ssh_host: '10.0.0.10', snapshot_path: '/tmp/snap.json' },
      has_credentials: true,
      timeout_seconds: 30,
      max_retries: 3,
      read_only: false,
      enabled: true,
      auto_sync: true,
      schema_version: 'v1',
    },
    {
      id: 2,
      name: 'file-src',
      connector_type: 'file',
      server_ci_id: null,
      config: { path: '/data/ci.json' },
      has_credentials: false,
      timeout_seconds: 30,
      max_retries: 3,
      read_only: false,
      enabled: false,
      auto_sync: false,
      schema_version: 'v1',
    },
    {
      id: 3,
      name: 'api-src',
      connector_type: 'api',
      server_ci_id: null,
      config: { url: 'https://cmdb.example/api' },
      has_credentials: false,
      timeout_seconds: 30,
      max_retries: 3,
      read_only: false,
      enabled: true,
      auto_sync: false,
      schema_version: 'v1',
    },
    {
      id: 4,
      name: 'db-src',
      connector_type: 'db',
      server_ci_id: null,
      config: { query: 'SELECT 1' },
      has_credentials: true,
      timeout_seconds: 30,
      max_retries: 3,
      read_only: false,
      enabled: true,
      auto_sync: false,
      schema_version: 'v1',
    },
    {
      id: 5,
      name: 'stream-src',
      connector_type: 'stream',
      server_ci_id: null,
      config: { topic: 'events' },
      has_credentials: false,
      timeout_seconds: 30,
      max_retries: 3,
      read_only: false,
      enabled: true,
      auto_sync: false,
      schema_version: 'v1',
    },
  ]
  return {
    ...actual,
    useQuery: () => ({
      data,
      isLoading: false,
    }),
    __setConnectorsMockData: (next: unknown[]) => {
      data = next
    },
  }
})

describe('ConnectorsTab', () => {
  it('renders connector table without horizontal overflow wrapper', () => {
    renderWithProviders(
      <ConnectorsTab
        canEdit
        onNew={vi.fn()}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onTest={vi.fn()}
        onSync={vi.fn()}
      />,
    )

    expect(screen.getAllByText('demo-host').length).toBeGreaterThan(0)
    expect(screen.getAllByText('file-src').length).toBeGreaterThan(0)
    expect(screen.getByText('https://cmdb.example/api')).toBeInTheDocument()
    expect(screen.getByTestId('connectors-table')).toBeInTheDocument()
    expect(document.querySelector('.connectors-table-fit')).toBeTruthy()
  })
})
