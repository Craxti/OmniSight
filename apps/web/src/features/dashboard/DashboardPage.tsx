import { Link } from 'react-router-dom'
import { Activity, Boxes, CheckCircle2, GitBranch, ShieldAlert } from 'lucide-react'
import { PageHeader, Skeleton } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { StatusDistributionChart } from '@/features/dashboard/components/StatusDistributionChart'
import { TypeDistributionChart } from '@/features/dashboard/components/TypeDistributionChart'
import { useDashboardPage } from '@/features/dashboard/hooks/useDashboardPage'
import type { IconTone } from '@/lib/iconTone'

export default function DashboardPage() {
  const { t } = useI18n()
  const { data, isLoading } = useDashboardPage()

  const health = data?.model_health
  const issueCount = health?.issue_count ?? 0
  const modelOk = health ? health.valid && issueCount === 0 : true

  return (
    <div className="space-y-6">
      <PageHeader title={t.dashboard.title} subtitle={t.dashboard.subtitle} />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading ? (
          [...Array(4)].map((_, i) => <Skeleton key={i} className="h-24 w-full" />)
        ) : (
          <>
            <StatCard icon={Boxes} label={t.dashboard.statCi} value={data?.total_ci ?? 0} tone="brand" />
            <StatCard icon={GitBranch} label={t.dashboard.statRelations} value={data?.total_relations ?? 0} tone="info" />
            <StatCard icon={ShieldAlert} label={t.dashboard.statActive} value={data?.by_status?.active ?? 0} tone="success" />
            <HealthCard
              modelOk={modelOk}
              issueCount={issueCount}
              title={t.dashboard.modelHealth}
              statusOk={t.dashboard.healthOk}
              statusIssues={t.dashboard.healthIssues}
              linkLabel={t.dashboard.validateLink}
            />
          </>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="mb-4 font-semibold text-[var(--text-primary)]">{t.dashboard.byType}</h2>
          {isLoading ? (
            <Skeleton className="h-60 w-full" />
          ) : (
            <TypeDistributionChart byType={data?.by_type ?? {}} emptyLabel={t.nav.noResults} />
          )}
        </div>
        <div className="card p-5">
          <h2 className="mb-4 font-semibold text-[var(--text-primary)]">{t.dashboard.byStatus}</h2>
          {isLoading ? (
            <Skeleton className="h-60 w-full" />
          ) : (
            <StatusDistributionChart
              byStatus={data?.by_status ?? {}}
              labels={t.common.ciStatus}
              emptyLabel={t.nav.noResults}
            />
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: typeof Boxes
  label: string
  value: number
  tone: IconTone
}) {
  return (
    <div className="card flex items-center gap-4 p-5">
      <div className={`stat-icon stat-icon--${tone}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div className="min-w-0">
        <div className="stat-card-value">{value}</div>
        <div className="text-sm text-[var(--text-muted)]">{label}</div>
      </div>
    </div>
  )
}

function HealthCard({
  modelOk,
  issueCount,
  title,
  statusOk,
  statusIssues,
  linkLabel,
}: {
  modelOk: boolean
  issueCount: number
  title: string
  statusOk: string
  statusIssues: string
  linkLabel: string
}) {
  const tone: IconTone = modelOk ? 'success' : 'warning'

  return (
    <Link
      to="/relations"
      className="card flex items-center gap-4 p-5 transition-colors hover:bg-[var(--bg-hover)]"
      title={linkLabel}
    >
      <div className={`stat-icon stat-icon--${tone}`}>
        {modelOk ? <CheckCircle2 className="h-6 w-6 text-white" /> : <Activity className="h-6 w-6 text-white" />}
      </div>
      <div className="min-w-0">
        <div className="stat-card-value">{issueCount}</div>
        <div className="text-sm text-[var(--text-muted)]">{title}</div>
        <div className={`mt-0.5 truncate text-xs ${modelOk ? 'text-success' : 'text-warning'}`}>
          {modelOk ? statusOk : statusIssues}
        </div>
      </div>
    </Link>
  )
}
