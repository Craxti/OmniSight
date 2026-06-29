import { Copy, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui'
import { useI18n } from '@/context/useI18n'
import { generatePassword } from '@/lib/password'
import { FormField } from '@/shared/components/FormField'

type Props = {
  label: string
  value: string
  onChange: (value: string) => void
  required?: boolean
  autoFocus?: boolean
}

export function PasswordField({ label, value, onChange, required, autoFocus }: Props) {
  const { t } = useI18n()

  return (
    <FormField label={label} htmlFor={label ? 'password-field' : undefined}>
      <div className="flex gap-2">
        <input
          id={label ? 'password-field' : undefined}
          className="input font-mono"
          type="text"
          autoFocus={autoFocus}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
        />
        <Button variant="secondary" className="shrink-0 px-3" onClick={() => onChange(generatePassword())} aria-label={t.settings.generatePassword}>
          <RefreshCw className="h-4 w-4" />
        </Button>
        <Button variant="secondary" className="shrink-0 px-3" onClick={() => navigator.clipboard.writeText(value)} aria-label={t.settings.copy}>
          <Copy className="h-4 w-4" />
        </Button>
      </div>
    </FormField>
  )
}
