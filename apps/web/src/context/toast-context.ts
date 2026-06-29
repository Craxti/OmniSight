import { createContext } from 'react'

type ToastType = 'success' | 'error' | 'info'

export interface ToastContextValue {
  toast: (message: string, type?: ToastType) => void
  success: (message: string) => void
  error: (message: string) => void
}

export const ToastContext = createContext<ToastContextValue | null>(null)
