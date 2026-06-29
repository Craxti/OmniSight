import { Link } from 'react-router-dom'
import { Modal } from '@/components/ui'
import { useAuth } from '@/context/useAuth'
import {
  useAutodiscoverModal,
  type AutodiscoverScopeDefaults,
} from '@/shared/components/autodiscover/hooks/useAutodiscoverModal'
import { AutodiscoverScanForm } from '@/shared/components/autodiscover/components/AutodiscoverScanForm'
import { AutodiscoverMappingReview } from '@/shared/components/autodiscover/components/AutodiscoverMappingReview'

export type { AutodiscoverScopeDefaults }

type Props = {
  open: boolean
  onClose: () => void
  onApplied: () => void
  scopeDefaults?: AutodiscoverScopeDefaults
}

export function AutodiscoverModal({ open, onClose, onApplied, scopeDefaults }: Props) {
  const { canEdit } = useAuth()
  const modal = useAutodiscoverModal({ open, scopeDefaults, onClose, onApplied })
  const {
    t,
    profileId,
    setProfileId,
    selectedServers,
    scopeMode,
    setScopeMode,
    scopeDepth,
    setScopeDepth,
    discoverRelations,
    setDiscoverRelations,
    createMissingCi,
    setCreateMissingCi,
    manualReview,
    setManualReview,
    mappingFilter,
    setMappingFilter,
    scanResult,
    selected,
    profiles,
    servers,
    serversLoading,
    connectors,
    filteredMappings,
    scanMut,
    applyMut,
    handleClose,
    toggleServer,
    toggleMapping,
    clearScanResult,
  } = modal

  if (!canEdit) return null

  return (
    <Modal open={open} onClose={handleClose} title={t.autodiscover.title} wide>
      <p className="mb-4 text-sm text-[var(--text-muted)]">{t.autodiscover.subtitle}</p>
      {(connectors ?? []).length === 0 && (
        <p className="alert alert-warning mb-4">
          {t.autodiscover.noConnectorsHint}{' '}
          <Link to="/settings" className="underline" onClick={handleClose}>{t.nav.settings}</Link>
        </p>
      )}

      {!scanResult ? (
        <AutodiscoverScanForm
          t={t}
          profileId={profileId}
          setProfileId={setProfileId}
          profiles={profiles}
          servers={servers}
          serversLoading={serversLoading}
          selectedServers={selectedServers}
          toggleServer={toggleServer}
          scopeMode={scopeMode}
          setScopeMode={setScopeMode}
          scopeDepth={scopeDepth}
          setScopeDepth={setScopeDepth}
          discoverRelations={discoverRelations}
          setDiscoverRelations={setDiscoverRelations}
          createMissingCi={createMissingCi}
          setCreateMissingCi={setCreateMissingCi}
          manualReview={manualReview}
          setManualReview={setManualReview}
          scanPending={scanMut.isPending}
          onCancel={handleClose}
          onScan={() => scanMut.mutate(undefined)}
        />
      ) : (
        <AutodiscoverMappingReview
          t={t}
          scanResult={scanResult}
          mappingFilter={mappingFilter}
          setMappingFilter={setMappingFilter}
          filteredMappings={filteredMappings}
          selected={selected}
          toggleMapping={toggleMapping}
          applyPending={applyMut.isPending}
          onBack={clearScanResult}
          onApply={() => applyMut.mutate(undefined)}
        />
      )}
    </Modal>
  )
}
