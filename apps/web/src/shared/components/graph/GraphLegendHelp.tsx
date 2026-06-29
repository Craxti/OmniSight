import { HelpCircle } from 'lucide-react'
import { useState } from 'react'

import { Modal } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { GraphLegendContent } from '@/shared/components/graph/GraphLegendContent'

export function GraphLegendHelp() {
  const { t } = useI18n()
  const [open, setOpen] = useState(false)
  const [hovered, setHovered] = useState(false)

  return (
    <>
      <div className="graph-legend-help pointer-events-none absolute right-3 top-3 z-20">
        <div className="pointer-events-auto relative">
          <button
            type="button"
            className="graph-legend-help-btn"
            aria-label={t.graph.legendHelpTitle}
            aria-expanded={open}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            onFocus={() => setHovered(true)}
            onBlur={() => setHovered(false)}
            onClick={() => setOpen(true)}
            data-testid="graph-legend-help"
          >
            <HelpCircle className="h-4 w-4" aria-hidden />
          </button>

          {hovered && !open ? (
            <div className="graph-legend-help-tooltip" role="tooltip">
              <p className="mb-2 text-xs font-medium text-[var(--text-primary)]">{t.graph.legendHelpTitle}</p>
              <GraphLegendContent compact />
              <p className="text-caption mt-2 border-t border-[var(--border-subtle)] pt-2 text-[var(--text-muted)]">
                {t.graph.legendHelpClick}
              </p>
            </div>
          ) : null}
        </div>
      </div>

      <Modal open={open} onClose={() => setOpen(false)} title={t.graph.legendHelpTitle} wide>
        <GraphLegendContent />
      </Modal>
    </>
  )
}
