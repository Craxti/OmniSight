import type { ExtendedExportFormat } from '@/shared/export/downloadByFormat'

export type ExportFormat = ExtendedExportFormat

export type ExportFilterState = {
  type_id: string
  environment: string
  owner: string
  criticality: string
  business_service_id: string
  service_code: string
}

export const defaultExportFilters: ExportFilterState = {
  type_id: '',
  environment: '',
  owner: '',
  criticality: '',
  business_service_id: '',
  service_code: '',
}
