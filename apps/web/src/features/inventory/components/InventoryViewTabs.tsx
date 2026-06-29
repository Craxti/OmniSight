import { useI18n } from '@/context/useI18n'
import { TabBar } from '@/shared/components/TabBar'

interface Props {
  view: 'active' | 'recycle'
  onChange: (view: 'active' | 'recycle') => void
}

export function InventoryViewTabs({ view, onChange }: Props) {
  const { t } = useI18n()

  return (
    <TabBar
      testId="inventory-view-tabs"
      ariaLabel={t.inventory.title}
      items={[
        { id: 'active' as const, label: t.inventory.active },
        { id: 'recycle' as const, label: t.inventory.recycle },
      ]}
      active={view}
      onChange={onChange}
    />
  )
}
