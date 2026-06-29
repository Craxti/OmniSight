import type { ComponentPropsWithoutRef } from 'react'
import * as LabelPrimitive from '@radix-ui/react-label'
import { cn } from '@/lib/utils'

type FieldLabelProps = ComponentPropsWithoutRef<typeof LabelPrimitive.Root> & {
  required?: boolean
}

export function FieldLabel({ className, children, required, ...props }: FieldLabelProps) {
  return (
    <LabelPrimitive.Root className={cn('label block', className)} {...props}>
      {children}
      {required ? <span className="text-error"> *</span> : null}
    </LabelPrimitive.Root>
  )
}
