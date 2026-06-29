import { Download, Plus, Upload, type LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'
import { Button, buttonClassName } from '@/components/ui'
import { IMPORT_FILE_ACCEPT } from '@/shared/export/formats'

export type ToolbarAction = {
  key: string
  label: string
  icon: LucideIcon
  onClick: () => void
  variant?: 'primary' | 'secondary'
  testId?: string
}

type Props = {
  exportLabel: string
  importLabel: string
  createLabel: string
  isAdmin: boolean
  canEdit: boolean
  onExport: () => void
  onImport?: (file: File) => void
  onCreate: () => void
  extraActions?: ToolbarAction[]
  importTestId?: string
  createTestId?: string
  trailing?: ReactNode
}

export function ImportExportToolbar({
  exportLabel,
  importLabel,
  createLabel,
  isAdmin,
  canEdit,
  onExport,
  onImport,
  onCreate,
  extraActions = [],
  importTestId,
  createTestId,
  trailing,
}: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button variant="secondary" onClick={onExport} data-testid="entity-export">
        <Download className="h-4 w-4" /> {exportLabel}
      </Button>
      {isAdmin && onImport && (
        <label className={buttonClassName('secondary', 'cursor-pointer')}>
          <Upload className="h-4 w-4" /> {importLabel}
          <input
            type="file"
            data-testid={importTestId}
            accept={IMPORT_FILE_ACCEPT}
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) onImport(file)
              e.target.value = ''
            }}
          />
        </label>
      )}
      {extraActions.map((action) => {
        const Icon = action.icon
        return (
          <Button
            key={action.key}
            variant={action.variant ?? 'secondary'}
            onClick={action.onClick}
            data-testid={action.testId}
          >
            <Icon className="h-4 w-4" /> {action.label}
          </Button>
        )
      })}
      {canEdit && (
        <Button variant="primary" onClick={onCreate} data-testid={createTestId}>
          <Plus className="h-4 w-4" /> {createLabel}
        </Button>
      )}
      {trailing}
    </div>
  )
}
