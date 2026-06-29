import { ChevronDown, ChevronRight } from 'lucide-react'
import { useMemo, useState, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

type JsonTreeViewProps = {
  value: unknown
  maxHeight?: string
  defaultExpandedDepth?: number
  className?: string
}

type NodeProps = {
  label?: string
  value: unknown
  depth: number
  defaultExpandedDepth: number
  path: string
}

function formatPrimitive(value: unknown): ReactNode {
  if (value === null) return <span className="json-tree-null">null</span>
  if (typeof value === 'string') return <span className="json-tree-string">"{value}"</span>
  if (typeof value === 'number') return <span className="json-tree-number">{String(value)}</span>
  if (typeof value === 'boolean') return <span className="json-tree-boolean">{String(value)}</span>
  return <span className="json-tree-null">{String(value)}</span>
}

function JsonNode({ label, value, depth, defaultExpandedDepth, path }: NodeProps) {
  const [open, setOpen] = useState(depth < defaultExpandedDepth)
  const isArray = Array.isArray(value)
  const isObject = value !== null && typeof value === 'object' && !isArray
  const isContainer = isArray || isObject

  if (!isContainer) {
    return (
      <div className="json-tree-line" data-path={path}>
        {label != null && (
          <>
            <span className="json-tree-key">{label}</span>
            <span className="json-tree-colon">: </span>
          </>
        )}
        {formatPrimitive(value)}
      </div>
    )
  }

  const entries = isArray
    ? (value as unknown[]).map((item, index) => [String(index), item] as const)
    : Object.entries(value as Record<string, unknown>)

  const openBracket = isArray ? '[' : '{'
  const closeBracket = isArray ? ']' : '}'
  const preview = isArray ? `${entries.length} items` : `${entries.length} keys`

  return (
    <div className="json-tree-node" data-path={path}>
      <div className="json-tree-line">
        <button
          type="button"
          className="json-tree-toggle focus-brand"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label={open ? 'Collapse' : 'Expand'}
        >
          {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
        </button>
        {label != null && (
          <>
            <span className="json-tree-key">{label}</span>
            <span className="json-tree-colon">: </span>
          </>
        )}
        <span className="json-tree-bracket">{openBracket}</span>
        {!open && (
          <>
            <span className="json-tree-preview"> {preview} </span>
            <span className="json-tree-bracket">{closeBracket}</span>
          </>
        )}
      </div>
      {open && (
        <div className="json-tree-children">
          {entries.map(([entryKey, entryValue]) => (
            <JsonNode
              key={`${path}.${entryKey}`}
              label={isArray ? undefined : entryKey}
              value={entryValue}
              depth={depth + 1}
              defaultExpandedDepth={defaultExpandedDepth}
              path={`${path}.${entryKey}`}
            />
          ))}
          <div className="json-tree-line">
            <span className="json-tree-bracket">{closeBracket}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export function JsonTreeView({
  value,
  maxHeight = '20rem',
  defaultExpandedDepth = 2,
  className,
}: JsonTreeViewProps) {
  const root = useMemo(() => value, [value])

  return (
    <div
      className={cn('json-tree-view code-block', className)}
      style={{ maxHeight }}
      data-testid="json-tree-view"
    >
      <div className="json-tree-root p-3">
        {root !== null && typeof root === 'object' ? (
          <JsonNode
            value={root}
            depth={0}
            defaultExpandedDepth={defaultExpandedDepth}
            path="root"
          />
        ) : (
          <div className="json-tree-line">{formatPrimitive(root)}</div>
        )}
      </div>
    </div>
  )
}
