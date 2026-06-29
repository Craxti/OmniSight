import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Relation } from '@/shared/api/types'

type Props = {
  relation: Relation
  perspectiveCiId: number
  perspectiveCiName?: string
  className?: string
}

export function RelationEndpointRow({ relation, perspectiveCiId, perspectiveCiName, className = '' }: Props) {
  const outgoing = relation.source_ci_id === perspectiveCiId

  return (
    <div className={`flex flex-wrap items-center gap-2 text-sm ${className}`.trim()}>
      {outgoing ? (
        <>
          <span className="font-medium text-[var(--text-primary)]">{perspectiveCiName ?? relation.source_name}</span>
          <ArrowRight className="h-4 w-4 text-info" />
          <Link to={`/inventory/${relation.target_ci_id}`} className="link">
            {relation.target_name}
          </Link>
        </>
      ) : (
        <>
          <Link to={`/inventory/${relation.source_ci_id}`} className="link">
            {relation.source_name}
          </Link>
          <ArrowRight className="h-4 w-4 text-info" />
          <span className="font-medium text-[var(--text-primary)]">{perspectiveCiName ?? relation.target_name}</span>
        </>
      )}
      <span className="badge badge-indigo ml-auto">{relation.relation_type}</span>
    </div>
  )
}
