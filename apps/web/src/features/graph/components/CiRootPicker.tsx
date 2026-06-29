import { ChevronDown, Search, X } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useI18n } from '@/context/useI18n'
import { cn } from '@/lib/utils'
import { useCiList } from '@/shared/hooks/useCiList'
import { useSearch } from '@/shared/hooks/useSearch'
import { FormField } from '@/shared/components/FormField'
import type { CI } from '@/shared/api/types'

type Props = {
  value: string
  onChange: (id: string) => void
}

function filterLocal(items: CI[], query: string): CI[] {
  const q = query.trim().toLowerCase()
  if (!q) return items.slice(0, 24)
  return items
    .filter(
      (ci) =>
        ci.name.toLowerCase().includes(q) ||
        (ci.type ?? '').toLowerCase().includes(q) ||
        String(ci.id).includes(q),
    )
    .slice(0, 24)
}

export function CiRootPicker({ value, onChange }: Props) {
  const { t } = useI18n()
  const wrapRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')

  const { data: cis, isLoading: listLoading } = useCiList()
  const { data: searchData, isFetching: searchLoading } = useSearch(query)

  const selected = useMemo(
    () => (cis?.items ?? []).find((c) => String(c.id) === value),
    [cis?.items, value],
  )

  const options: CI[] = useMemo(() => {
    if (query.trim().length >= 2) return searchData?.cis ?? []
    return filterLocal(cis?.items ?? [], query)
  }, [query, searchData?.cis, cis?.items])

  const loading = open && (query.trim().length >= 2 ? searchLoading : listLoading)

  const inputValue = open ? query : selected ? `${selected.name} (${selected.type})` : ''

  useEffect(() => {
    if (!open) return
    const onDoc = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onDoc)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDoc)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  const openPicker = () => {
    setOpen(true)
    setQuery('')
    requestAnimationFrame(() => inputRef.current?.focus())
  }

  const pick = (ci: CI) => {
    onChange(String(ci.id))
    setQuery('')
    setOpen(false)
  }

  const clear = () => {
    onChange('')
    setQuery('')
    setOpen(false)
  }

  return (
    <FormField label={t.graph.root} htmlFor="graph-root-search" className="relative">
      <div ref={wrapRef} className="relative">
        <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 z-10 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
        <input
          ref={inputRef}
          id="graph-root-search"
          data-testid="graph-root-search"
          className="input input--with-icons w-full"
          placeholder={t.graph.selectCi}
          value={inputValue}
          readOnly={!open && !!selected}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={openPicker}
          onClick={() => {
            if (!open) openPicker()
          }}
        />
        <div className="absolute top-1/2 right-1 flex -translate-y-1/2 items-center gap-0.5">
          {value ? (
            <button
              type="button"
              className="rounded p-1 text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]"
              onClick={(e) => {
                e.stopPropagation()
                clear()
              }}
              aria-label={t.common.cancel}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          ) : null}
          <button
            type="button"
            className="rounded p-1 text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]"
            onClick={(e) => {
              e.stopPropagation()
              if (open) setOpen(false)
              else openPicker()
            }}
            aria-expanded={open}
            aria-label={t.graph.selectCi}
          >
            <ChevronDown className={cn('h-4 w-4 transition-transform', open && 'rotate-180')} />
          </button>
        </div>
      </div>

      {open ? (
        <div className="absolute top-[calc(100%-0.25rem)] right-0 left-0 z-[100] mt-1 overflow-hidden rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-popover)] shadow-2xl ring-1 ring-black/20">
          <div className="max-h-56 overflow-y-auto">
            {loading ? (
              <div className="px-3 py-3 text-sm text-[var(--text-muted)]">{t.common.loading}</div>
            ) : options.length === 0 ? (
              <div className="px-3 py-3 text-sm text-[var(--text-muted)]">{t.common.notFound}</div>
            ) : (
              options.map((ci) => {
                const active = String(ci.id) === value
                return (
                  <button
                    key={ci.id}
                    type="button"
                    data-testid={`graph-root-option-${ci.id}`}
                    className={cn(
                      'flex w-full flex-col items-start gap-0.5 border-b border-[var(--border-subtle)] px-3 py-2.5 text-left last:border-0',
                      'hover:bg-[var(--bg-hover)]',
                      active && 'bg-[var(--rsm-color-brand-muted)]',
                    )}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => pick(ci)}
                  >
                    <span
                      className={cn(
                        'truncate text-sm font-medium',
                        active ? 'text-info' : 'text-[var(--text-primary)]',
                      )}
                    >
                      {ci.name}
                    </span>
                    <span className="truncate text-xs text-[var(--text-muted)]">
                      {ci.type} · #{ci.id}
                    </span>
                  </button>
                )
              })
            )}
          </div>
          {query.trim().length === 1 ? (
            <div className="text-caption border-t border-[var(--border-subtle)] px-3 py-2 text-[var(--text-muted)]">
              {t.graph.searchMinChars}
            </div>
          ) : null}
        </div>
      ) : null}
      </div>
    </FormField>
  )
}
