import { useState } from 'react'

import { Modal } from '@/components/ui'

import { FormField } from '@/shared/components/FormField'

import { FormModalActions } from '@/shared/components/FormModalActions'

import type { ExtendedExportFormat } from '@/shared/export/downloadByFormat'

import { EXTENDED_EXPORT_FORMATS } from '@/shared/export/formats'



type Props = {

  open: boolean

  title: string

  formatLabel: string

  cancelLabel: string

  submitLabel: string

  defaultFormat?: ExtendedExportFormat

  onClose: () => void

  onExport: (format: ExtendedExportFormat) => void | Promise<void>

}



export function ExportFormatModal({

  open,

  title,

  formatLabel,

  cancelLabel,

  submitLabel,

  defaultFormat = 'xlsx',

  onClose,

  onExport,

}: Props) {

  const [format, setFormat] = useState<ExtendedExportFormat>(defaultFormat)



  return (

    <Modal open={open} onClose={onClose} title={title} testId="export-format-modal">

      <div className="space-y-3">

        <FormField label={formatLabel}>

          <select className="input" value={format} data-testid="export-format-select" onChange={(e) => setFormat(e.target.value as ExtendedExportFormat)}>

            {EXTENDED_EXPORT_FORMATS.map((opt) => (

              <option key={opt.value} value={opt.value}>

                {opt.label}

              </option>

            ))}

          </select>

        </FormField>

      </div>

      <FormModalActions

        onCancel={onClose}

        onSubmit={() => void onExport(format)}

        submitLabel={submitLabel}

        cancelLabel={cancelLabel}

        submitTestId="export-format-submit"

      />

    </Modal>

  )

}


