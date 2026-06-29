const TOKEN_KEY = 'omnisight_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function parseApiError(res: Response, fallback: string): Promise<string> {
  let detail = fallback || res.statusText
  try {
    const body = (await res.json()) as { detail?: unknown }
    detail = body.detail != null ? String(body.detail) : JSON.stringify(body)
  } catch {
    try {
      detail = await res.text()
    } catch {
      /* ignore */
    }
  }
  return String(detail)
}

function handleUnauthorized(res: Response, token: string | null) {
  if (res.status === 401 && token) {
    clearToken()
    window.dispatchEvent(new Event('auth:unauthorized'))
  }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(path, { ...options, headers })
  handleUnauthorized(res, token)
  if (!res.ok) {
    throw new ApiError(res.status, await parseApiError(res, res.statusText))
  }
  if (res.status === 204) return undefined as T
  const text = await res.text()
  if (!text.trim()) return undefined as T
  return JSON.parse(text) as T
}

/** Omit null, undefined, and empty-string entries (keeps 0 and false). */
export function omitBlank<T extends Record<string, unknown>>(obj: T): Partial<T> {
  return Object.fromEntries(Object.entries(obj).filter(([, v]) => v != null && v !== '')) as Partial<T>
}

/** @deprecated Use `omitBlank` — same semantics (null, undefined, empty string). */
export const omitEmpty = omitBlank

/** Append all query params (used for list/search endpoints). */
export function buildQuery(params?: Record<string, string | number>): string {
  if (!params) return ''
  const q = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => q.set(k, String(v)))
  const s = q.toString()
  return s ? `?${s}` : ''
}

/** Skip empty/null/undefined params (used for export/download endpoints). */
export function buildExportQuery(params?: Record<string, string | number>): string {
  if (!params) return ''
  const filtered = omitBlank(params as Record<string, unknown>)
  const q = new URLSearchParams()
  Object.entries(filtered).forEach(([k, v]) => q.set(k, String(v)))
  const s = q.toString()
  return s ? `?${s}` : ''
}

export async function uploadFile<T>(path: string, file: File, fieldName = 'file'): Promise<T> {
  const fd = new FormData()
  fd.append(fieldName, file)
  const token = getToken()
  const res = await fetch(path, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: fd,
  })
  handleUnauthorized(res, token)
  if (!res.ok) throw new ApiError(res.status, await parseApiError(res, res.statusText))
  return res.json() as Promise<T>
}

export async function downloadFile(
  path: string,
  filename: string,
  params?: Record<string, string | number>,
): Promise<void> {
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${path}${buildExportQuery(params)}`, { headers })
  handleUnauthorized(res, token)
  if (!res.ok) {
    throw new ApiError(res.status, await parseApiError(res, res.statusText))
  }

  const blob = await res.blob()
  downloadBlob(blob, filename)
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
