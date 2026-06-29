import { zodResolver } from '@hookform/resolvers/zod'
import { Radar } from 'lucide-react'
import { Button } from '@/components/ui'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import type { useI18n } from '@/context/useI18n'
import type { CI, CIList } from '@/shared/api/types'
import { FormField } from '@/shared/components/FormField'
import { ListRowsSkeleton } from '@/components/ui'
import { BilingualFieldHelp } from '@/shared/components/BilingualFieldHelp'
import { autodiscoverProfileHelp, autodiscoverScopeHelp } from '@/i18n/locales/autodiscoverHelp'
import { autodiscoverScanSchema, type AutodiscoverScanValues } from '@/lib/forms/schemas/settingsSchemas'

type Messages = ReturnType<typeof useI18n>['t']

type Props = {
  t: Messages
  profileId: number | ''
  setProfileId: (id: number | '') => void
  profiles: Array<{ id: number; name: string }> | undefined
  servers: Pick<CIList, 'items'> | undefined
  serversLoading: boolean
  selectedServers: number[]
  toggleServer: (id: number) => void
  scopeMode: 'graph' | 'all' | 'filters'
  setScopeMode: (mode: 'graph' | 'all' | 'filters') => void
  scopeDepth: number
  setScopeDepth: (depth: number) => void
  discoverRelations: boolean
  setDiscoverRelations: (value: boolean) => void
  createMissingCi: boolean
  setCreateMissingCi: (value: boolean) => void
  manualReview: boolean
  setManualReview: (value: boolean) => void
  scanPending: boolean
  onCancel: () => void
  onScan: () => void
}

export function AutodiscoverScanForm({
  t,
  profileId,
  setProfileId,
  profiles,
  servers,
  serversLoading,
  selectedServers,
  toggleServer,
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
  scanPending,
  onCancel,
  onScan,
}: Props) {
  const values: AutodiscoverScanValues = {
    profileId,
    selectedServers,
    scopeMode,
    scopeDepth,
    discoverRelations,
    createMissingCi,
    manualReview,
  }

  const {
    reset,
    handleSubmit,
    setError,
    clearErrors,
    formState: { errors },
  } = useForm<AutodiscoverScanValues>({
    resolver: zodResolver(autodiscoverScanSchema),
    values,
  })

  useEffect(() => {
    reset({
      profileId,
      selectedServers,
      scopeMode,
      scopeDepth,
      discoverRelations,
      createMissingCi,
      manualReview,
    })
    clearErrors()
  }, [
    profileId,
    selectedServers,
    scopeMode,
    scopeDepth,
    discoverRelations,
    createMissingCi,
    manualReview,
    reset,
    clearErrors,
  ])

  const submit = handleSubmit(() => onScan(), (fieldErrors) => {
    Object.entries(fieldErrors).forEach(([key, err]) => {
      if (err?.message) setError(key as keyof AutodiscoverScanValues, { message: err.message })
    })
  })

  return (
    <form onSubmit={submit} className="space-y-4">
      <FormField
        label={t.autodiscover.profile}
        htmlFor="autodiscover-profile"
        labelAction={<BilingualFieldHelp section={autodiscoverProfileHelp} testId="autodiscover-profile-help" />}
      >
        <select
          id="autodiscover-profile"
          className="input"
          value={profileId}
          onChange={(e) => setProfileId(e.target.value ? Number(e.target.value) : '')}
        >
          <option value="">{t.autodiscover.defaultProfile}</option>
          {(profiles ?? []).map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </FormField>

      <FormField label={t.autodiscover.sources} error={errors.selectedServers?.message}>
        {serversLoading ? (
          <ListRowsSkeleton rows={4} />
        ) : (servers?.items ?? []).length === 0 ? (
          <p className="text-sm text-[var(--text-muted)]">{t.autodiscover.noServers}</p>
        ) : (
          <ul className="max-h-40 space-y-1 overflow-y-auto rounded-lg border border-[var(--border-subtle)] p-2">
            {(servers?.items ?? []).map((srv: CI) => {
              const host = srv.external_ids?.hostname ?? srv.attributes?.hostname
              return (
                <li key={srv.id}>
                  <label className="flex cursor-pointer items-start gap-2 rounded px-2 py-1.5 hover:bg-[var(--bg-hover)]">
                    <input
                      type="checkbox"
                      className="mt-0.5"
                      checked={selectedServers.includes(srv.id)}
                      onChange={() => toggleServer(srv.id)}
                      data-testid={`autodiscover-server-${srv.id}`}
                    />
                    <span className="text-sm">
                      <span className="font-medium text-[var(--text-primary)]">{srv.name}</span>
                      {host ? <span className="text-[var(--text-muted)]"> · {String(host)}</span> : null}
                    </span>
                  </label>
                </li>
              )
            })}
          </ul>
        )}
      </FormField>

      <div className="grid gap-3 sm:grid-cols-2">
        <FormField
          label={t.autodiscover.scopeMode}
          htmlFor="autodiscover-scope-mode"
          labelAction={<BilingualFieldHelp section={autodiscoverScopeHelp} testId="autodiscover-scope-help" />}
        >
          <select id="autodiscover-scope-mode" className="input" value={scopeMode} onChange={(e) => setScopeMode(e.target.value as typeof scopeMode)}>
            <option value="graph">{t.autodiscover.scopeGraph}</option>
            <option value="all">{t.autodiscover.scopeAll}</option>
            <option value="filters">{t.autodiscover.scopeFilters}</option>
          </select>
        </FormField>
        {scopeMode === 'graph' ? (
          <FormField label={t.autodiscover.scopeDepth} htmlFor="autodiscover-depth">
            <input
              id="autodiscover-depth"
              className="input"
              type="number"
              min={0}
              max={5}
              value={scopeDepth}
              onChange={(e) => setScopeDepth(Number(e.target.value))}
            />
          </FormField>
        ) : null}
      </div>

      <div className="space-y-2 rounded-lg border border-[var(--border-subtle)] p-3">
        <label className="flex cursor-pointer items-center gap-2 text-sm">
          <input type="checkbox" checked={discoverRelations} onChange={(e) => setDiscoverRelations(e.target.checked)} />
          {t.autodiscover.discoverRelations}
        </label>
        <label className="flex cursor-pointer items-center gap-2 text-sm">
          <input type="checkbox" checked={createMissingCi} onChange={(e) => setCreateMissingCi(e.target.checked)} />
          {t.autodiscover.createMissingCi}
        </label>
        <label className="flex cursor-pointer items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={manualReview}
            onChange={(e) => setManualReview(e.target.checked)}
            data-testid="autodiscover-manual-review"
          />
          {t.autodiscover.manualReview}
        </label>
        <p className="hint">{t.autodiscover.relationsHint}</p>
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="secondary" className="min-h-11 sm:min-h-0" onClick={onCancel}>{t.common.cancel}</Button>
        <Button
          type="submit"
          variant="primary"
          className="min-h-11 sm:min-h-0"
          disabled={scanPending}
          data-testid="autodiscover-scan"
        >
          <Radar className="h-4 w-4" />
          {scanPending
            ? (manualReview ? t.autodiscover.scanning : t.autodiscover.syncing)
            : (manualReview ? t.autodiscover.scan : t.autodiscover.sync)}
        </Button>
      </div>
    </form>
  )
}
