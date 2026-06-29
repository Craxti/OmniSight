import * as XLSX from 'xlsx'
import { parse as parseYaml } from 'yaml'

const SPREADSHEET_EXTENSIONS = new Set(['xlsx', 'xls', 'xlsm', 'xlsb', 'csv'])
const YAML_EXTENSIONS = new Set(['yaml', 'yml'])

function extensionOf(fileName: string): string {
  const idx = fileName.lastIndexOf('.')
  return idx >= 0 ? fileName.slice(idx + 1).toLowerCase() : ''
}

function workbookToRows(workbook: XLSX.WorkBook): unknown[] {
  const firstSheetName = workbook.SheetNames[0]
  if (!firstSheetName) return []
  const sheet = workbook.Sheets[firstSheetName]
  if (!sheet) return []
  return XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet, { defval: '' })
}

function parseXmlItems(text: string): unknown[] {
  const doc = new DOMParser().parseFromString(text, 'application/xml')
  if (doc.querySelector('parsererror')) {
    throw new Error('Invalid XML file')
  }

  const root = doc.documentElement
  if (!root) return []

  const preferred = Array.from(root.querySelectorAll(':scope > item, :scope > row, :scope > record, :scope > element'))
  const entries = preferred.length > 0 ? preferred : Array.from(root.children)

  return entries.map((entry) => {
    const obj: Record<string, unknown> = {}
    if (entry.children.length === 0) {
      obj.value = entry.textContent?.trim() ?? ''
      return obj
    }
    for (const child of Array.from(entry.children)) {
      obj[child.tagName] = child.textContent?.trim() ?? ''
    }
    return obj
  })
}

function extractItems(parsed: unknown): unknown[] {
  if (Array.isArray(parsed)) return parsed
  if (!parsed || typeof parsed !== 'object') return []
  const data = parsed as { items?: unknown[]; elements?: unknown[]; relations?: unknown[] }
  return data.items || data.elements || data.relations || []
}

export async function parseImportFile(file: File): Promise<unknown[]> {
  const ext = extensionOf(file.name)

  if (SPREADSHEET_EXTENSIONS.has(ext)) {
    const bytes = await file.arrayBuffer()
    const workbook = XLSX.read(bytes, { type: 'array' })
    return workbookToRows(workbook)
  }

  if (ext === 'json') {
    return extractItems(JSON.parse(await file.text()))
  }

  if (ext === 'xml') {
    return parseXmlItems(await file.text())
  }

  if (YAML_EXTENSIONS.has(ext)) {
    return extractItems(parseYaml(await file.text()))
  }

  throw new Error('Unsupported import format')
}

