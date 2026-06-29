import { useCallback, useState, type ReactNode } from 'react'
import { CheckCircle2, XCircle, X } from 'lucide-react'
import { Button } from '@/components/ui'
import { cn } from '@/lib/utils'
import { ToastContext } from '@/context/toast-context'
import { useI18n } from '@/context/useI18n'

type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: number
  message: string
  type: ToastType
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const { t } = useI18n()
  const [toasts, setToasts] = useState<Toast[]>([])

  const remove = (id: number) => setToasts((prev) => prev.filter((x) => x.id !== id))

  const toast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Date.now()
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => remove(id), 4000)
  }, [])

  const success = useCallback((message: string) => toast(message, 'success'), [toast])
  const error = useCallback((message: string) => toast(message, 'error'), [toast])

  return (
    <ToastContext.Provider value={{ toast, success, error }}>
      {children}
      <div
        className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2"
        role="status"
        aria-live="polite"
        aria-relevant="additions"
        aria-label={t.common.notifications}
      >
        {toasts.map((item) => (
          <div
            key={item.id}
            className={cn(
              'toast-item flex items-center gap-3 rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md',
              item.type === 'success' && 'toast-success',
              item.type === 'error' && 'toast-error',
              item.type === 'info' && 'toast-info',
            )}
          >
            {item.type === 'success' ? <CheckCircle2 className="h-4 w-4 shrink-0" aria-hidden /> : item.type === 'error' ? <XCircle className="h-4 w-4 shrink-0" aria-hidden /> : null}
            <span className="text-sm">{item.message}</span>
            <Button variant="ghost" onClick={() => remove(item.id)} className="ml-2 !border-0 !bg-transparent !p-1 opacity-60 hover:opacity-100" aria-label={t.common.close}>
              <X className="h-3 w-3" aria-hidden />
            </Button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
