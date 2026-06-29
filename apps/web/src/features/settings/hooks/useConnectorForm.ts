import { useQuery } from '@tanstack/react-query'
import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useMemo } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { useI18n } from '@/context/useI18n'
import { ciApi } from '@/shared/api/ci'
import type { SyncConnector, SyncConnectorInput } from '@/shared/api/autodiscover'
import { SERVER_TYPE_NAME } from '@/shared/constants'
import { useCiTypes } from '@/shared/hooks/useCiTypes'
import { queryKeys } from '@/shared/queryKeys'
import {
  buildConnectorSubmitPayload,
  connectorFormFromInitial,
  EMPTY_CONNECTOR_FORM,
  parseSshHostTarget,
  type ConnectorFormState,
} from '@/features/settings/connectorFormState'
import { createConnectorFormSchema } from '@/lib/forms/schemas/settingsSchemas'

export function useConnectorForm(
  open: boolean,
  initial: SyncConnector | null | undefined,
  onSubmit: (body: SyncConnectorInput, form: ConnectorFormState) => void,
) {
  const { t } = useI18n()
  const schema = createConnectorFormSchema(t)

  const {
    watch,
    setValue,
    reset,
    handleSubmit,
    formState: { errors },
  } = useForm<ConnectorFormState>({
    resolver: zodResolver(schema) as Resolver<ConnectorFormState>,
    defaultValues: EMPTY_CONNECTOR_FORM,
  })

  const form = watch()

  const { data: types } = useCiTypes({ enabled: open })
  const serverTypeId = useMemo(() => types?.find((tp) => tp.name === SERVER_TYPE_NAME)?.id, [types])
  const { data: servers } = useQuery({
    queryKey: [...queryKeys.ci.all, 'servers', serverTypeId],
    queryFn: () => ciApi.list({ type_id: serverTypeId!, limit: 200 }),
    enabled: open && !!serverTypeId,
  })

  useEffect(() => {
    if (!open) return
    reset(initial ? connectorFormFromInitial(initial) : EMPTY_CONNECTOR_FORM)
  }, [open, initial, reset])

  const isHost = form.connector_type === 'host'
  const serverItems = servers?.items ?? []

  useEffect(() => {
    if (!open || !isHost || form.server_ci_mode !== 'existing' || form.server_ci_id || !serverItems.length) return
    const target = form.ssh_host.trim().toLowerCase()
    if (!target) return
    const match = serverItems.find((srv) => {
      const ip = String(srv.external_ids?.ip ?? srv.attributes?.ip ?? '').toLowerCase()
      const host = String(srv.external_ids?.hostname ?? srv.attributes?.hostname ?? '').toLowerCase()
      return ip === target || host === target
    })
    if (match) setValue('server_ci_id', String(match.id))
  }, [open, isHost, form.server_ci_mode, form.server_ci_id, form.ssh_host, serverItems, setValue])

  useEffect(() => {
    if (!open || !isHost || form.server_ci_mode !== 'new') return
    const { hostname, ip } = parseSshHostTarget(form.ssh_host)
    if (hostname && hostname !== form.new_server_hostname) setValue('new_server_hostname', hostname)
    if (ip && ip !== form.new_server_ip) setValue('new_server_ip', ip)
    const suggestedName = form.name.trim() || hostname || ip
    if (suggestedName && !form.new_server_name.trim()) setValue('new_server_name', suggestedName)
  }, [open, isHost, form.server_ci_mode, form.ssh_host, form.name, form.new_server_hostname, form.new_server_ip, form.new_server_name, setValue])

  const saveBlockedReason =
    errors.name?.message
    ?? errors.server_ci_id?.message
    ?? errors.new_server_name?.message
    ?? errors.new_server_hostname?.message
    ?? errors.new_server_ip?.message
    ?? null

  const setForm = (next: ConnectorFormState | ((prev: ConnectorFormState) => ConnectorFormState)) => {
    const value = typeof next === 'function' ? next(form) : next
    reset(value)
  }

  const submit = handleSubmit((data) => onSubmit(buildConnectorSubmitPayload(data), data))

  return {
    form,
    setForm,
    isHost,
    serverItems,
    saveBlockedReason,
    submit,
    errors,
  }
}
