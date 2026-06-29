import type { QueryClient } from '@tanstack/react-query'
import { queryKeys } from '@/shared/queryKeys'

export function invalidateCiQueries(qc: QueryClient) {
  void qc.invalidateQueries({ queryKey: queryKeys.ci.all })
}

export function invalidateCiTypesQueries(qc: QueryClient) {
  void qc.invalidateQueries({ queryKey: queryKeys.ci.types })
}

export function invalidateRelationsQueries(qc: QueryClient) {
  void qc.invalidateQueries({ queryKey: queryKeys.relations.all })
}

export function invalidateGraphQueries(qc: QueryClient, rootId: number, depth: number) {
  void qc.invalidateQueries({ queryKey: queryKeys.relations.all })
  void qc.invalidateQueries({ queryKey: queryKeys.graph(rootId, depth) })
  void qc.invalidateQueries({ queryKey: queryKeys.businessPath(rootId) })
  void qc.invalidateQueries({ queryKey: queryKeys.impact(rootId) })
  void qc.invalidateQueries({ queryKey: queryKeys.relations.validate })
  invalidateCiQueries(qc)
}

export function invalidateInventoryAfterImport(qc: QueryClient) {
  invalidateCiQueries(qc)
  invalidateCiTypesQueries(qc)
}
