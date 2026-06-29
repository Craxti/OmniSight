import { Zap } from 'lucide-react'
import type { CIResponse } from '@/shared/api/types.generated'
import { useI18n } from '@/context/useI18n'
import { ciTypeLabel } from '@/lib/domainLabels'
import { getCiTypeVisual } from '@/lib/graphVisuals'

type Props = {
  items: CIResponse[]
  title: string
}

export function RootCauseZoneCards({ items, title }: Props) {
  const { t } = useI18n()

  return (
    <section className="correlation-root-cause-zone" data-testid="correlation-root-cause-zone">
      <h3 className="correlation-root-cause-zone__title">
        <Zap className="h-5 w-5 text-warning" aria-hidden />
        {title}
      </h3>
      <p className="correlation-root-cause-zone__hint">{t.correlation.rootCauseZoneHint}</p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((ci) => {
          const typeName = String(ci.type ?? '')
          const visual = getCiTypeVisual(typeName)
          const Icon = visual.icon
          const meta = [typeName ? ciTypeLabel(t, typeName) : null, ci.environment ? String(ci.environment) : null]
            .filter(Boolean)
            .join(' · ')

          return (
            <article
              key={ci.id}
              className="correlation-root-cause-card"
              data-testid={`correlation-root-cause-ci-${ci.id}`}
            >
              <div
                className="correlation-root-cause-card__icon"
                style={{ backgroundColor: visual.iconBg, color: visual.accent }}
                aria-hidden
              >
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <div className="correlation-root-cause-card__name">{ci.name}</div>
                {meta ? <div className="correlation-root-cause-card__meta">{meta}</div> : null}
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}
