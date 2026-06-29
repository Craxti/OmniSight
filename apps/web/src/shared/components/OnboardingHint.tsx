import { Lightbulb, X } from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { useI18n } from '@/context/useI18n'

type Props = {
  storageKey: string
  title: string
  children: ReactNode
}

export function OnboardingHint({ storageKey, title, children }: Props) {
  const { t } = useI18n()
  const [dismissed, setDismissed] = useState(() => {
    try {
      return localStorage.getItem(storageKey) === '1'
    } catch {
      return false
    }
  })

  if (dismissed) return null

  const dismiss = () => {
    try {
      localStorage.setItem(storageKey, '1')
    } catch {
      /* ignore quota / private mode */
    }
    setDismissed(true)
  }

  return (
    <div className="onboarding-hint alert alert-info" role="note" data-testid={`onboarding-${storageKey}`}>
      <Lightbulb className="onboarding-hint__icon h-5 w-5 shrink-0" aria-hidden />
      <div className="min-w-0 flex-1">
        <div className="font-medium text-[var(--alert-info-text)]">{title}</div>
        <div className="onboarding-hint__body mt-1.5 text-sm text-[var(--text-muted)]">{children}</div>
      </div>
      <button
        type="button"
        className="onboarding-hint__dismiss focus-brand"
        onClick={dismiss}
        aria-label={t.common.dismissHint}
      >
        <X className="h-4 w-4" aria-hidden />
      </button>
    </div>
  )
}
