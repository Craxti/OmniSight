import { useApiMutation } from '@/shared/hooks/useApiMutation'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '@/context/useAuth'
import { useI18n } from '@/context/useI18n'
import { ciApi, miscApi } from '@/shared/api'
import { BUSINESS_SERVICE_TYPE_NAME } from '@/shared/constants'
import type { CiEditFormState } from '@/features/inventory/components/CiEditForm'
import { useCiResourcePanels } from '@/shared/hooks/useCiResourcePanels'
import { queryKeys } from '@/shared/queryKeys'

export type CiDetailTab = 'overview' | 'relations' | 'components' | 'impact' | 'history'

export function useCiDetailPage() {
  const { id } = useParams()
  const ciId = Number(id)
  const { canEdit } = useAuth()
  const { t, dateLocale } = useI18n()
  const [tab, setTab] = useState<CiDetailTab>('overview')
  const [edit, setEdit] = useState(false)
  const [form, setForm] = useState<CiEditFormState>({
    name: '',
    description: '',
    status: 'active',
    criticality: '',
    environment: '',
    owner: '',
    team: '',
  })

  const { data: ci, isLoading } = useQuery({
    queryKey: queryKeys.ci.detail(ciId),
    queryFn: () => ciApi.get(ciId),
    enabled: !!ciId,
  })

  const { data: relations } = useQuery({
    queryKey: queryKeys.ci.relations(ciId),
    queryFn: () => ciApi.relations(ciId),
    enabled: tab === 'relations' && !!ciId,
  })

  const { components, impact } = useCiResourcePanels(ciId, {
    components: tab === 'components' && !!ciId,
    impact: tab === 'impact' && !!ciId,
    isBusinessService: ci?.type === BUSINESS_SERVICE_TYPE_NAME,
  })

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: queryKeys.ci.audit(ciId),
    queryFn: () => miscApi.entityAudit('ci', ciId),
    enabled: tab === 'history' && !!ciId,
  })

  const updateMut = useApiMutation({
    mutationFn: (data: CiEditFormState) => ciApi.update(ciId, data),
    invalidateKeys: [queryKeys.ci.detail(ciId), queryKeys.ci.audit(ciId)],
    messages: { success: t.ciDetail.toastSaved, error: t.common.error },
    onSuccess: () => setEdit(false),
  })

  const startEdit = () => {
    if (!ci) return
    setForm({
      name: ci.name,
      description: ci.description || '',
      status: ci.status,
      criticality: ci.criticality || '',
      environment: ci.environment || '',
      owner: ci.owner || '',
      team: ci.team || '',
    })
    setEdit(true)
  }

  return {
    ciId,
    ci,
    isLoading,
    canEdit,
    t,
    dateLocale,
    tab,
    setTab,
    edit,
    setEdit,
    form,
    setForm,
    relations,
    components,
    impact,
    history,
    historyLoading,
    updateMut,
    startEdit,
  }
}
