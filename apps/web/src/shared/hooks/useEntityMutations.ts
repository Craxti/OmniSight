import { type QueryKey, useQueryClient } from '@tanstack/react-query'
import { useApiMutation } from '@/shared/hooks/useApiMutation'

type IdMutationOptions = {
  mutationFn: (id: number) => Promise<unknown>
  invalidateKeys: QueryKey[]
  messages: { success: string; error: string }
}

/** Factory for standard delete/restore/purge mutations by entity id. */
export function useEntityIdMutation({ mutationFn, invalidateKeys, messages }: IdMutationOptions) {
  return useApiMutation({
    mutationFn,
    invalidateKeys,
    messages,
  })
}

type InvalidateFn = () => void

/** Returns a callback that invalidates the given query keys. */
export function useInvalidateKeys(keys: QueryKey[]): InvalidateFn {
  const qc = useQueryClient()
  return () => {
    for (const key of keys) {
      void qc.invalidateQueries({ queryKey: key })
    }
  }
}
