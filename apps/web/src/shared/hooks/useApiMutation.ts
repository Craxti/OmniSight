import { useMutation, useQueryClient, type QueryKey } from '@tanstack/react-query'
import { useToast } from '@/context/useToast'

type Messages = {
  success: string
  error: string
}

type Options<TData, TVariables> = {
  mutationFn: (variables: TVariables) => Promise<TData>
  invalidateKeys?: QueryKey[]
  messages: Messages
  getSuccessMessage?: (data: TData, variables: TVariables) => string
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (err: unknown) => void
  /** When false, skip automatic success/error toasts (caller handles feedback). */
  notify?: boolean
}

/** Standard mutation wrapper: invalidate cache keys + toast feedback. */
export function useApiMutation<TData, TVariables>({
  mutationFn,
  invalidateKeys = [],
  messages,
  getSuccessMessage,
  onSuccess,
  onError,
  notify = true,
}: Options<TData, TVariables>) {
  const qc = useQueryClient()
  const { success, error } = useToast()

  return useMutation({
    mutationFn,
    onSuccess: (data, variables) => {
      for (const key of invalidateKeys) {
        void qc.invalidateQueries({ queryKey: key })
      }
      if (notify) {
        success(getSuccessMessage ? getSuccessMessage(data, variables) : messages.success)
      }
      onSuccess?.(data, variables)
    },
    onError: (err) => {
      if (onError) {
        onError(err)
        return
      }
      if (notify) {
        error(err instanceof Error ? err.message : messages.error)
      }
    },
  })
}
