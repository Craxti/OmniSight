import { useMemo, type ReactNode } from 'react'

const TOKEN_RE =
  /("(?:\\.|[^"\\])*")|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|(\btrue\b|\bfalse\b)|(\bnull\b)|([{}[\],:])/g

export function highlightJsonText(json: string): ReactNode[] {
  const nodes: ReactNode[] = []
  let last = 0
  let key = 0

  for (const match of json.matchAll(TOKEN_RE)) {
    const index = match.index ?? 0
    if (index > last) {
      nodes.push(json.slice(last, index))
    }

    const [token, stringLit, numberLit, boolLit, nullLit, punct] = match
    if (stringLit) {
      const isKey = /^\s*:/.test(json.slice(index + token.length))
      nodes.push(
        <span key={key++} className={isKey ? 'json-tree-key' : 'json-tree-string'}>
          {token}
        </span>,
      )
    } else if (numberLit) {
      nodes.push(
        <span key={key++} className="json-tree-number">
          {token}
        </span>,
      )
    } else if (boolLit) {
      nodes.push(
        <span key={key++} className="json-tree-boolean">
          {token}
        </span>,
      )
    } else if (nullLit) {
      nodes.push(
        <span key={key++} className="json-tree-null">
          {token}
        </span>,
      )
    } else if (punct) {
      nodes.push(
        <span key={key++} className="json-tree-bracket">
          {token}
        </span>,
      )
    }

    last = index + token.length
  }

  if (last < json.length) {
    nodes.push(json.slice(last))
  }

  return nodes
}

export function useHighlightedJson(value: unknown): ReactNode[] {
  const raw = JSON.stringify(value, null, 2)
  return useMemo(() => highlightJsonText(raw), [raw])
}
