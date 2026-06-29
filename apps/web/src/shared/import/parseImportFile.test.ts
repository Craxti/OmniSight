import * as XLSX from 'xlsx'
import { describe, expect, it } from 'vitest'
import { parseImportFile } from '@/shared/import/parseImportFile'

function makeFile(parts: BlobPart[], name: string, type = 'application/octet-stream') {
  return new File(parts, name, { type })
}

describe('parseImportFile', () => {
  it('parses spreadsheet formats', async () => {
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet([{ name: 'demo', type: 'Application' }])
    XLSX.utils.book_append_sheet(wb, ws, 'elements')
    const bytes = XLSX.write(wb, { type: 'array', bookType: 'xlsx' }) as ArrayBuffer

    for (const ext of ['xlsx', 'xls', 'xlsm', 'xlsb']) {
      const file = makeFile([bytes], `import.${ext}`)
      const rows = await parseImportFile(file)
      expect(Array.isArray(rows)).toBe(true)
      expect(rows.length).toBeGreaterThan(0)
    }

    const csvRows = await parseImportFile(makeFile(['name,type\ndemo,Application\n'], 'import.csv', 'text/csv'))
    expect(csvRows).toHaveLength(1)
  })

  it('parses json, xml and yaml formats', async () => {
    const jsonRows = await parseImportFile(makeFile([JSON.stringify([{ a: 1 }])], 'import.json', 'application/json'))
    expect(jsonRows).toHaveLength(1)

    const xmlRows = await parseImportFile(
      makeFile(['<?xml version="1.0"?><export><item><source_name>a</source_name></item></export>'], 'import.xml', 'application/xml'),
    )
    expect(xmlRows).toHaveLength(1)

    const yamlRows = await parseImportFile(makeFile(['- source_name: a\n  target_name: b\n'], 'import.yaml', 'application/yaml'))
    expect(yamlRows).toHaveLength(1)

    const ymlRows = await parseImportFile(makeFile(['relations:\n  - relation_type: depends_on\n'], 'import.yml', 'application/yaml'))
    expect(ymlRows).toHaveLength(1)
  })
})

