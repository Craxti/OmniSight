import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useToast } from '@/context/useToast'
import { useI18n } from '@/context/useI18n'
import { mergeAttributesToExternal } from '@/features/inventory/inventoryForm'
import type { ConnectorFormState } from '@/features/settings/connectorFormState'
import { useConnectorsMutations } from '@/features/settings/hooks/useConnectorsMutations'
import { ciApi } from '@/shared/api/ci'
import type { SyncConnector, SyncConnectorInput } from '@/shared/api/autodiscover'
import {
  DEFAULT_CI_STATUS,
  DEFAULT_CRITICALITY,
  DEFAULT_ENVIRONMENT,
  SERVER_TYPE_NAME,
} from '@/shared/constants'
import { queryKeys } from '@/shared/queryKeys'

export function useConnectorsSettings() {
  const { t } = useI18n()
  const { error } = useToast()
  const queryClient = useQueryClient()
  const [connectorForm, setConnectorForm] = useState<SyncConnector | null | undefined>(undefined)
  const [deleteConnector, setDeleteConnector] = useState<SyncConnector | null>(null)
  const [submittingConnector, setSubmittingConnector] = useState(false)

  const {
    createMut: createConnectorMut,
    updateMut: updateConnectorMut,
    deleteMut: deleteConnectorMut,
    testMut,
    syncMut,
  } = useConnectorsMutations()

  const submitConnector = async (body: SyncConnectorInput, form: ConnectorFormState) => {
    setSubmittingConnector(true)
    let createdServerCi = false
    try {
      let payload = body
      if (form.connector_type === 'host' && form.server_ci_mode === 'new') {
        const { attributes, external_ids } = mergeAttributesToExternal({
          hostname: form.new_server_hostname.trim(),
          ip: form.new_server_ip.trim(),
          port: form.ssh_port.trim() || '22',
          os: 'Linux',
        })
        const ci = await ciApi.create({
          name: form.new_server_name.trim(),
          type_name: SERVER_TYPE_NAME,
          status: DEFAULT_CI_STATUS,
          criticality: DEFAULT_CRITICALITY,
          environment: DEFAULT_ENVIRONMENT,
          owner: form.ssh_user.trim() || 'admin',
          attributes,
          external_ids,
        })
        createdServerCi = true
        payload = { ...payload, server_ci_id: ci.id }
        await queryClient.invalidateQueries({ queryKey: queryKeys.ci.all })
      }

      if (connectorForm?.id) {
        await updateConnectorMut.mutateAsync({ id: connectorForm.id, body: payload })
      } else {
        await createConnectorMut.mutateAsync(payload)
      }
      setConnectorForm(undefined)
    } catch {
      if (form.connector_type === 'host' && form.server_ci_mode === 'new' && !createdServerCi) {
        error(t.common.error)
      }
    } finally {
      setSubmittingConnector(false)
    }
  }

  return {
    connectorForm,
    setConnectorForm,
    deleteConnector,
    setDeleteConnector,
    createConnectorMut,
    updateConnectorMut,
    deleteConnectorMut,
    testMut,
    syncMut,
    submitConnector,
    submittingConnector,
  }
}
