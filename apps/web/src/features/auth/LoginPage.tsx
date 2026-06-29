import { zodResolver } from '@hookform/resolvers/zod'
import { Activity } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { FormField } from '@/shared/components/FormField'
import { createLoginSchema } from '@/lib/forms/schemas/authSchemas'

export default function LoginPage() {
  const { login } = useAuth()
  const { t } = useI18n()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState('')
  const schema = createLoginSchema(t)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: import.meta.env.PROD
      ? { email: '', password: '' }
      : { email: 'admin@omnisight.local', password: 'admin123' },
  })

  const submit = handleSubmit(async ({ email, password }) => {
    setServerError('')
    try {
      const me = await login(email, password)
      navigate(me.must_change_password ? '/change-password' : '/')
    } catch (err) {
      setServerError(err instanceof Error ? err.message : t.login.error)
    }
  })

  return (
    <div className="relative flex min-h-full items-center justify-center overflow-hidden p-4">
      <div className="auth-page-glow-top" />
      <div className="auth-page-glow-blur -left-32 top-20" />
      <div className="auth-page-glow-blur -right-32 bottom-20" />

      <div className="card relative w-full max-w-md p-6 shadow-2xl sm:p-8">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="brand-icon brand-icon--lg mb-4">
            <Activity className="h-7 w-7 text-white" />
          </div>
          <h1 className="page-title">OmniSight</h1>
          <p className="mt-1 text-sm text-[var(--text-muted)]">{t.login.subtitle}</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <FormField label="Email" htmlFor="login-email" error={errors.email?.message}>
            <input id="login-email" className="input" type="email" autoComplete="username" {...register('email')} />
          </FormField>
          <FormField label={t.login.password} htmlFor="login-password" error={errors.password?.message}>
            <input id="login-password" className="input" type="password" autoComplete="current-password" {...register('password')} />
          </FormField>
          {serverError && <div className="alert alert-error text-sm" role="alert">{serverError}</div>}
          <Button type="submit" variant="primary" fullWidth className="py-3 sm:py-2.5" disabled={isSubmitting} data-testid="login-submit">
            {isSubmitting ? t.login.signingIn : t.login.signIn}
          </Button>
        </form>
        <p className="mt-6 text-center text-xs text-[var(--text-muted)]">{t.login.hint}</p>
      </div>
    </div>
  )
}
