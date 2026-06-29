import { describe, expect, it, vi } from 'vitest'
import { buildExportQuery, buildQuery } from '@/shared/api/client'

describe('client query helpers', () => {
  it('buildQuery encodes all params', () => {
    expect(buildQuery({ q: 'hello world', page: 2 })).toBe('?q=hello+world&page=2')
    expect(buildQuery()).toBe('')
  })

  it('buildExportQuery skips empty values', () => {
    expect(buildExportQuery({ a: 'x', b: '', c: 0 })).toBe('?a=x&c=0')
  })
})

describe('uploadFile', () => {
  it('posts multipart and returns json', async () => {
    const { uploadFile } = await import('./client')
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ imported: 1 }),
    })
    vi.stubGlobal('fetch', fetchMock)
    vi.stubGlobal('localStorage', { getItem: () => 'tok' })

    const result = await uploadFile<{ imported: number }>('/api/v1/ci/import/csv', new File(['a'], 'a.csv'))
    expect(result.imported).toBe(1)
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/ci/import/csv',
      expect.objectContaining({ method: 'POST' }),
    )
    vi.unstubAllGlobals()
  })
})
