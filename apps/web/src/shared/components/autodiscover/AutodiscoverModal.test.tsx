import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AutodiscoverModal } from '@/shared/components/autodiscover/AutodiscoverModal'
import { messages } from '@/i18n/messages'
import { renderWithProviders } from '@/test/renderWithProviders'

vi.mock('@/context/useAuth', () => ({
  useAuth: () => ({ canEdit: true }),
}))

vi.mock('@/shared/components/autodiscover/hooks/useAutodiscoverModal', () => ({
  useAutodiscoverModal: () => ({
    t: messages.en,
    profileId: '',
    setProfileId: vi.fn(),
    selectedServers: [],
    scopeMode: 'all',
    setScopeMode: vi.fn(),
    scopeDepth: 1,
    setScopeDepth: vi.fn(),
    discoverRelations: true,
    setDiscoverRelations: vi.fn(),
    createMissingCi: true,
    setCreateMissingCi: vi.fn(),
    manualReview: true,
    setManualReview: vi.fn(),
    mappingFilter: 'all',
    setMappingFilter: vi.fn(),
    scanResult: null,
    selected: new Set<string>(),
    profiles: [],
    servers: [],
    serversLoading: false,
    connectors: [{ id: 1, name: 'local' }],
    filteredMappings: [],
    scanMut: { mutate: vi.fn(), isPending: false },
    applyMut: { mutate: vi.fn(), isPending: false },
    handleClose: vi.fn(),
    toggleServer: vi.fn(),
    toggleMapping: vi.fn(),
    clearScanResult: vi.fn(),
  }),
}))

describe('AutodiscoverModal', () => {
  it('renders scan step when open', () => {
    renderWithProviders(
      <AutodiscoverModal open onClose={vi.fn()} onApplied={vi.fn()} scopeDefaults={{ scope_mode: 'all' }} />,
    )
    expect(screen.getByText(messages.en.autodiscover.title)).toBeInTheDocument()
    expect(screen.getByText(messages.en.autodiscover.subtitle)).toBeInTheDocument()
  })
})
