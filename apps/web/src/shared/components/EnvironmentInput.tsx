import { useDomainConstants } from '@/shared/hooks/useDomainConstants'

type Props = {
  value: string
  onChange: (value: string) => void
  id?: string
  className?: string
  placeholder?: string
  'data-testid'?: string
  allowEmpty?: boolean
}

export function EnvironmentInput({
  value,
  onChange,
  id = 'env-input',
  className = 'input',
  placeholder,
  'data-testid': testId,
  allowEmpty,
}: Props) {
  const { environments } = useDomainConstants()
  const listId = `${id}-presets`

  return (
    <div>
      <input
        id={id}
        list={listId}
        className={className}
        value={value}
        placeholder={placeholder}
        data-testid={testId}
        onChange={(e) => onChange(e.target.value)}
      />
      <datalist id={listId}>
        {allowEmpty ? <option value="" /> : null}
        {environments.map((env) => (
          <option key={env} value={env} />
        ))}
      </datalist>
    </div>
  )
}
