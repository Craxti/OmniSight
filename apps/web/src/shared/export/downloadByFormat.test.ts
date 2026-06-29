import { afterEach, describe, expect, it, vi } from 'vitest'
import { downloadByFormat } from '@/shared/export/downloadByFormat'

const { writeFileMock } = vi.hoisted(() => ({ writeFileMock: vi.fn() }))
vi.mock('xlsx', async (importOriginal) => {
  const mod = await importOriginal<typeof import('xlsx')>()
  return {
    ...mod,
    writeFile: writeFileMock,
  }
})

describe('downloadByFormat', () => {
  const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:test')
  const revokeObjectURL = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})

  afterEach(() => {
    createObjectURL.mockClear()
    revokeObjectURL.mockClear()
    writeFileMock.mockClear()
  })

  it('exports all non-excel formats via Blob download', () => {
    const payload = { elements: [{ name: 'demo' }], relations: [{ relation_type: 'depends_on' }] }
    for (const format of ['json', 'csv', 'xml', 'yaml', 'yml'] as const) {
      downloadByFormat(payload, format, 'test-export')
    }
    expect(createObjectURL).toHaveBeenCalledTimes(5)
  })

  it('exports all excel formats with XLSX writer', () => {
    const payload = { elements: [{ name: 'demo' }], relations: [] }
    for (const format of ['xlsx', 'xls', 'xlsm', 'xlsb'] as const) {
      downloadByFormat(payload, format, 'test-export')
    }
    expect(writeFileMock).toHaveBeenCalledTimes(4)
    expect(writeFileMock.mock.calls.map((c) => c[1])).toEqual([
      'test-export.xlsx',
      'test-export.xls',
      'test-export.xlsm',
      'test-export.xlsb',
    ])
  })
})

