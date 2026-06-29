import { zodResolver } from '@hookform/resolvers/zod'

import { Activity } from 'lucide-react'

import { useForm } from 'react-hook-form'

import { useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/useAuth'

import { useI18n } from '@/context/useI18n'

import { FormField } from '@/shared/components/FormField'

import { Button } from '@/components/ui'

import { authApi } from '@/shared/api'

import { createChangePasswordSchema } from '@/lib/forms/schemas/authSchemas'



export default function ChangePasswordPage() {

  const { user, refreshUser } = useAuth()

  const { t } = useI18n()

  const navigate = useNavigate()

  const schema = createChangePasswordSchema(t)



  const {

    register,

    handleSubmit,

    setError,

    formState: { errors, isSubmitting },

  } = useForm({

    resolver: zodResolver(schema),

    defaultValues: { currentPassword: '', newPassword: '', confirmPassword: '' },

  })



  const submit = handleSubmit(async ({ currentPassword, newPassword }) => {

    try {

      await authApi.changePassword(currentPassword, newPassword)

      await refreshUser()

      navigate('/', { replace: true })

    } catch (err) {

      setError('root', {

        message: err instanceof Error ? err.message : t.common.error,

      })

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

          <h1 className="page-title">{t.changePassword.title}</h1>

          <p className="page-subtitle">{t.changePassword.subtitle}</p>

          {user?.email && <p className="mt-1 text-xs text-[var(--text-muted)]">{user.email}</p>}

        </div>

        <form onSubmit={submit} className="space-y-4">

          <FormField label={t.changePassword.current} htmlFor="current-password" error={errors.currentPassword?.message}>

            <input

              id="current-password"

              className="input"

              type="password"

              autoComplete="current-password"

              autoFocus

              {...register('currentPassword')}

            />

          </FormField>

          <FormField label={t.changePassword.new} htmlFor="new-password" error={errors.newPassword?.message}>

            <input

              id="new-password"

              className="input"

              type="password"

              autoComplete="new-password"

              {...register('newPassword')}

            />

          </FormField>

          <FormField label={t.changePassword.confirm} htmlFor="confirm-password" error={errors.confirmPassword?.message}>

            <input

              id="confirm-password"

              className="input"

              type="password"

              autoComplete="new-password"

              {...register('confirmPassword')}

            />

          </FormField>

          {errors.root?.message && (

            <div className="alert alert-error text-sm" role="alert">{errors.root.message}</div>

          )}

          <Button type="submit" variant="primary" fullWidth className="py-3 sm:py-2.5" disabled={isSubmitting}>

            {isSubmitting ? t.changePassword.saving : t.changePassword.submit}

          </Button>

        </form>

      </div>

    </div>

  )

}

