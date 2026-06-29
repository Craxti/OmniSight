import { useState } from 'react'
import { useI18n } from '@/context/useI18n'
import { useHighlightedJson } from '@/lib/highlightJson'
import { cn } from '@/lib/utils'
import { JsonTreeView } from '@/shared/components/JsonTreeView'

type JsonViewerProps = {
  value: unknown
  maxHeight?: string
  className?: string
}

export function JsonViewer({ value, maxHeight = '20rem', className }: JsonViewerProps) {
  const { t } = useI18n()
  const [mode, setMode] = useState<'tree' | 'raw'>('tree')
  const highlighted = useHighlightedJson(value)

  return (
    <div className={cn('space-y-2', className)}>
      <div className="json-viewer-tabs" role="tablist" aria-label={t.correlation.jsonTitle}>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'tree'}
          data-active={mode === 'tree'}
          onClick={() => setMode('tree')}
        >
          {t.correlation.jsonViewTree}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'raw'}
          data-active={mode === 'raw'}
          onClick={() => setMode('raw')}
        >
          {t.correlation.jsonViewRaw}
        </button>
      </div>
      {mode === 'tree' ? (
        <JsonTreeView value={value} maxHeight={maxHeight} />
      ) : (
        <pre
          className="code-block overflow-auto p-3 text-xs"
          style={{ maxHeight }}
          data-testid="json-raw-view"
        >
          <code className="json-raw">{highlighted}</code>
        </pre>
      )}
    </div>
  )
}
