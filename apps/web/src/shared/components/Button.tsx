import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

export type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'ghost'
  | 'danger'
  | 'table'
  | 'table-primary'
  | 'table-warn'
  | 'table-danger'

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: 'btn btn-primary',
  secondary: 'btn btn-secondary',
  ghost: 'btn btn-ghost',
  danger: 'btn btn-danger',
  table: 'table-action-btn',
  'table-primary': 'table-action-btn table-action-btn--primary',
  'table-warn': 'table-action-btn table-action-btn--warn',
  'table-danger': 'table-action-btn table-action-btn--danger',
}

export function buttonClassName(
  variant: ButtonVariant = 'primary',
  className?: string,
  options?: { iconOnly?: boolean; fullWidth?: boolean },
) {
  return cn(
    VARIANT_CLASS[variant],
    options?.iconOnly && variant.startsWith('table') && 'table-action-btn--icon',
    options?.fullWidth && 'w-full',
    className,
  )
}

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant
  iconOnly?: boolean
  fullWidth?: boolean
  children?: ReactNode
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = 'primary', iconOnly, fullWidth, className, type = 'button', children, ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      className={buttonClassName(variant, className, { iconOnly, fullWidth })}
      {...props}
    >
      {children}
    </button>
  )
})
