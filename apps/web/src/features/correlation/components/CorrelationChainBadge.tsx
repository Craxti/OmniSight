import { CheckCircle2, Split } from 'lucide-react'
import { useI18n } from '@/context/useI18n'
import { cn } from '@/lib/utils'

type Props = {
  chainRelated: boolean
}

export function CorrelationChainBadge({ chainRelated }: Props) {
  const { t } = useI18n()
  const Icon = chainRelated ? CheckCircle2 : Split

  return (
    <div
      className={cn(
        'correlation-incident-badge',
        chainRelated ? 'correlation-incident-badge--single' : 'correlation-incident-badge--separate',
      )}
      data-testid="correlation-chain-related"
      data-chain-related={String(chainRelated)}
      role="status"
    >
      <Icon className="h-6 w-6 shrink-0" aria-hidden />
      <span>{chainRelated ? t.correlation.incidentSingle : t.correlation.incidentSeparate}</span>
    </div>
  )
}
