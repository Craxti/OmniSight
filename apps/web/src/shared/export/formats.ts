import type { ExtendedExportFormat } from '@/shared/export/downloadByFormat'

export const EXTENDED_EXPORT_FORMATS: { value: ExtendedExportFormat; label: string }[] = [
  { value: 'json', label: 'JSON' },
  { value: 'xlsx', label: 'XLSX' },
  { value: 'xls', label: 'XLS' },
  { value: 'xlsm', label: 'XLSM' },
  { value: 'xlsb', label: 'XLSB' },
  { value: 'csv', label: 'CSV' },
  { value: 'xml', label: 'XML' },
  { value: 'yaml', label: 'YAML' },
  { value: 'yml', label: 'YML' },
]

export const IMPORT_FILE_ACCEPT = '.xlsx,.xls,.xlsm,.xlsb,.csv,.json,.xml,.yaml,.yml'
