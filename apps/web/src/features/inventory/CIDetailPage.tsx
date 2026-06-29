import { ArrowLeft, Save } from 'lucide-react'
import { Link } from 'react-router-dom'
import { PageHeader, DetailPageSkeleton, ListRowsSkeleton, Button, buttonClassName } from '@/components/ui'
import { AuditHistoryList } from '@/shared/components/AuditHistoryList'
import { RelationEndpointRow } from '@/shared/components/RelationEndpointRow'
import { TabBar } from '@/shared/components/TabBar'
import { BUSINESS_SERVICE_TYPE_NAME } from '@/shared/constants'
import { criticalityBadge, statusBadge } from '@/lib/utils'
import { ciStatusLabel, criticalityLabel, externalIdFieldLabel } from '@/lib/domainLabels'
import { CiEditForm } from '@/features/inventory/components/CiEditForm'
import { useCiDetailPage } from '@/features/inventory/hooks/useCiDetailPage'

export default function CIDetailPage() {
  const {
    ciId,
    ci,
    isLoading,
    canEdit,
    t,
    dateLocale,
    tab,
    setTab,
    edit,
    form,
    setForm,
    relations,
    components,
    impact,
    history,
    historyLoading,
    updateMut,
    startEdit,
  } = useCiDetailPage()

  if (isLoading) return <DetailPageSkeleton />
  if (!ci) return <div className="text-[var(--text-muted)]">{t.ciDetail.notFound}</div>

  const tabs: { id: typeof tab; label: string; show?: boolean }[] = [
    { id: 'overview', label: t.ciDetail.tabOverview },
    { id: 'relations', label: t.ciDetail.tabRelations },
    { id: 'components', label: t.ciDetail.tabComponents, show: ci.type === BUSINESS_SERVICE_TYPE_NAME },
    { id: 'impact', label: t.ciDetail.tabImpact },
    { id: 'history', label: t.ciDetail.tabHistory },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/inventory" className={buttonClassName('secondary')}><ArrowLeft className="h-4 w-4" /></Link>
        <PageHeader
          className="flex-1"
          title={ci.name}
          subtitle={`${ci.type ?? ''} · #${ci.id}`}
          actions={
            canEdit && !edit ? (
              <Button variant="primary" onClick={startEdit}>{t.common.edit}</Button>
            ) : undefined
          }
        />
      </div>

      <div className="flex flex-wrap items-center gap-2 border-b border-[var(--border-subtle)] pb-2">
        <TabBar
          ariaLabel={t.ciDetail.tabOverview}
          items={tabs}
          active={tab}
          onChange={setTab}
        />
        <Link to={`/graph?root=${ciId}`} className="ml-auto link text-sm">{t.ciDetail.openOnMap}</Link>
      </div>

      {tab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-2">
          {edit ? (
            <>
              <CiEditForm form={form} onChange={setForm} />
              <div className="lg:col-span-2">
                <Button variant="primary" onClick={() => updateMut.mutate(form)}>
                  <Save className="h-4 w-4" /> {t.common.save}
                </Button>
              </div>
            </>
          ) : (
            <>
              <div className="card space-y-3 p-5">
                <h2 className="font-semibold text-[var(--text-primary)]">{t.ciDetail.main}</h2>
                <Row label={t.ciDetail.status}><span className={`badge ${statusBadge(ci.status)}`}>{ciStatusLabel(t, ci.status)}</span></Row>
                <Row label={t.ciDetail.criticality}><span className={`badge ${criticalityBadge(ci.criticality)}`}>{ci.criticality ? criticalityLabel(t, ci.criticality) : t.nav.noResults}</span></Row>
                <Row label={t.ciDetail.environment}>{ci.environment || t.nav.noResults}</Row>
                <Row label={t.ciDetail.owner}>{ci.owner || t.nav.noResults}</Row>
                <Row label={t.ciDetail.team}>{ci.team || t.nav.noResults}</Row>
                <Row label={t.ciDetail.changed}>{ci.last_changed_at ? new Date(ci.last_changed_at).toLocaleString(dateLocale) : t.nav.noResults}</Row>
                <Row label="description">{ci.description || t.nav.noResults}</Row>
              </div>
              <div className="card space-y-3 p-5">
                <h2 className="font-semibold text-[var(--text-primary)]">{t.ciDetail.externalIds}</h2>
                {Object.entries({ ...ci.external_ids, ...ci.attributes }).filter(([, v]) => v).map(([k, v]) => (
                  <Row key={k} label={externalIdFieldLabel(t, k)}>{String(v)}</Row>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {tab === 'relations' && (
        <div className="card p-5">
          <h2 className="mb-4 font-semibold text-[var(--text-primary)]">{t.ciDetail.elementRelations}</h2>
          {(relations || []).length === 0 ? (
            <p className="text-[var(--text-muted)]">{t.ciDetail.noRelations}</p>
          ) : (
            <div className="space-y-2">
              {(relations || []).map((r) => (
                <div key={r.id} className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] px-4 py-3">
                  <RelationEndpointRow relation={r} perspectiveCiId={ciId} perspectiveCiName={ci.name} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'components' && (
        <div className="card p-5">
          <h2 className="mb-4 font-semibold text-[var(--text-primary)]">{t.ciDetail.componentsTitle}</h2>
          <p className="mb-3 text-sm text-[var(--text-muted)]">{t.common.total}: {components?.count ?? 0}</p>
          <ul className="space-y-2">
            {(components?.components || []).map((c) => (
              <li key={c.id}><Link to={`/inventory/${c.id}`} className="link">{c.name}</Link> <span className="text-xs text-[var(--text-muted)]">{c.type}</span></li>
            ))}
          </ul>
        </div>
      )}

      {tab === 'impact' && (
        <div className="card p-5">
          <h2 className="mb-4 font-semibold text-[var(--text-primary)]">{t.ciDetail.impactTitle}</h2>
          {(impact?.impacted_business_services || []).length === 0 ? (
            <p className="text-[var(--text-muted)]">{t.ciDetail.noImpact}</p>
          ) : (
            <ul className="space-y-2">
              {(impact?.impacted_business_services || []).map((s: { id: number; name: string }) => (
                <li key={s.id}><Link to={`/inventory/${s.id}`} className="link">{s.name}</Link></li>
              ))}
            </ul>
          )}
        </div>
      )}

      {tab === 'history' && (
        <div className="card space-y-3 p-5">
          {historyLoading ? (
            <ListRowsSkeleton rows={3} />
          ) : (
            <AuditHistoryList entries={history ?? []} />
          )}
        </div>
      )}
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 text-sm">
      <span className="text-[var(--text-muted)]">{label}</span>
      <span className="text-right text-[var(--text-primary)]">{children}</span>
    </div>
  )
}
