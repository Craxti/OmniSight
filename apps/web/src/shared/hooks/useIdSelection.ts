import { useState } from 'react'

export function useIdSelection(itemIds: number[]) {
  const [selected, setSelected] = useState<Set<number>>(new Set())

  const toggleAll = () => {
    if (selected.size === itemIds.length) setSelected(new Set())
    else setSelected(new Set(itemIds))
  }

  const toggleOne = (id: number) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelected(next)
  }

  const clearSelection = () => setSelected(new Set())

  return { selected, setSelected, toggleAll, toggleOne, clearSelection }
}
