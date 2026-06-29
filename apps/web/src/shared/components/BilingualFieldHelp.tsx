import { HelpCircle } from 'lucide-react'
import { useState } from 'react'

import { Modal } from '@/components/ui'
import type { BilingualHelpSection } from '@/i18n/locales/autodiscoverHelp'
import { useI18n } from '@/context/useI18n'

type Props = {
  section: BilingualHelpSection
  testId?: string
}

function BilingualBlock({ ru, en }: { ru: string; en: string }) {
  return (
    <div className="space-y-1">
      <p className="text-sm text-[var(--text-primary)]">{ru}</p>
      <p className="text-sm text-[var(--text-muted)]">{en}</p>
    </div>
  )
}

export function BilingualFieldHelp({ section, testId }: Props) {
  const { locale, t } = useI18n()
  const [open, setOpen] = useState(false)
  const title = section.title[locale]

  return (
    <>
      <button
        type="button"
        className="inline-flex shrink-0 items-center justify-center rounded-full p-0.5 text-[var(--text-muted)] transition-colors hover:text-[var(--text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
        aria-label={t.common.help}
        onClick={() => setOpen(true)}
        data-testid={testId}
      >
        <HelpCircle className="h-3.5 w-3.5" aria-hidden />
      </button>

      <Modal open={open} onClose={() => setOpen(false)} title={title} wide>
        <div className="space-y-4">
          <BilingualBlock ru={section.intro.ru} en={section.intro.en} />
          <ul className="space-y-4">
            {section.items.map((item) => (
              <li key={`${item.label.en}-${item.label.ru}`} className="rounded-lg border border-[var(--border-subtle)] p-3">
                <p className="mb-2 text-sm font-medium text-[var(--text-primary)]">
                  {item.label.ru}
                  <span className="font-normal text-[var(--text-muted)]"> / {item.label.en}</span>
                </p>
                <BilingualBlock ru={item.description.ru} en={item.description.en} />
              </li>
            ))}
          </ul>
        </div>
      </Modal>
    </>
  )
}
