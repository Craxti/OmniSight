import * as XLSX from 'xlsx'
import { stringify as toYaml } from 'yaml'

export type ExtendedExportFormat = 'json' | 'xlsx' | 'xls' | 'xlsm' | 'xlsb' | 'csv' | 'xml' | 'yaml' | 'yml'

function triggerDownload(blob: Blob, filename: string) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}

function toXml(value: unknown, root = 'export'): string {
  const esc = (s: string) =>
    s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;')

  const render = (v: unknown, tag: string): string => {
    if (Array.isArray(v)) return `<${tag}>${v.map((x) => render(x, 'item')).join('')}</${tag}>`
    if (v && typeof v === 'object') {
      const obj = v as Record<string, unknown>
      return `<${tag}>${Object.entries(obj).map(([k, x]) => render(x, k)).join('')}</${tag}>`
    }
    return `<${tag}>${esc(v == null ? '' : String(v))}</${tag}>`
  }

  return `<?xml version="1.0" encoding="UTF-8"?>\n${render(value, root)}`
}

function workbookFromPayload(payload: unknown): XLSX.WorkBook {
  const wb = XLSX.utils.book_new()
  if (payload && typeof payload === 'object' && !Array.isArray(payload)) {
    const obj = payload as Record<string, unknown>
    const elements = Array.isArray(obj.elements) ? obj.elements : []
    const relations = Array.isArray(obj.relations) ? obj.relations : []
    if (elements.length) XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(elements as Record<string, unknown>[]), 'elements')
    if (relations.length) XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(relations as Record<string, unknown>[]), 'relations')
    if (!elements.length && !relations.length) {
      XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet([obj]), 'data')
    }
    return wb
  }
  const rows = Array.isArray(payload) ? payload : [payload]
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(rows as Record<string, unknown>[]), 'data')
  return wb
}

export function downloadByFormat(payload: unknown, format: ExtendedExportFormat, baseName: string) {
  if (format === 'json') {
    triggerDownload(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }), `${baseName}.json`)
    return
  }
  if (format === 'yaml' || format === 'yml') {
    triggerDownload(new Blob([toYaml(payload)], { type: 'application/yaml' }), `${baseName}.${format}`)
    return
  }
  if (format === 'xml') {
    triggerDownload(new Blob([toXml(payload)], { type: 'application/xml' }), `${baseName}.xml`)
    return
  }
  const wb = workbookFromPayload(payload)
  if (format === 'csv') {
    const first = wb.SheetNames[0]
    const csv = first ? XLSX.utils.sheet_to_csv(wb.Sheets[first]) : ''
    triggerDownload(new Blob([csv], { type: 'text/csv;charset=utf-8' }), `${baseName}.csv`)
    return
  }
  XLSX.writeFile(wb, `${baseName}.${format}`, { bookType: format })
}

