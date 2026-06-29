import { useState } from 'react'

import { Modal } from '@/components/ui'

import { EnvironmentInput } from '@/shared/components/EnvironmentInput'

import { FormField } from '@/shared/components/FormField'

import { useI18n } from '@/context/useI18n'

import { useDomainConstants } from '@/shared/hooks/useDomainConstants'
import { criticalityLabel } from '@/lib/domainLabels'

import { EXTENDED_EXPORT_FORMATS } from '@/shared/export/formats'

import { FormModalActions } from '@/shared/components/FormModalActions'

import type { ExportFilterState, ExportFormat } from '@/features/inventory/inventoryExport'

export type { ExportFilterState, ExportFormat } from '@/features/inventory/inventoryExport'



interface CiTypeOption {

  id: number

  name: string

}



interface BusinessServiceOption {

  id: number

  name: string

}



interface InventoryExportModalProps {

  open: boolean

  filters: ExportFilterState

  types?: CiTypeOption[]

  businessServices?: BusinessServiceOption[]

  onClose: () => void

  onChange: (filters: ExportFilterState) => void

  onExport: (format: ExportFormat) => void

}



export function InventoryExportModal({

  open,

  filters,

  types,

  businessServices,

  onClose,

  onChange,

  onExport,

}: InventoryExportModalProps) {

  const { t } = useI18n()

  const { criticalityLevels } = useDomainConstants()

  const [format, setFormat] = useState<ExportFormat>('json')



  return (

    <Modal open={open} onClose={onClose} title={t.inventory.exportModal}>

      <div className="space-y-3">

        <FormField label={t.inventory.exportFormat}>

          <select className="input" value={format} data-testid="inventory-export-format" onChange={(e) => setFormat(e.target.value as ExportFormat)}>

            {EXTENDED_EXPORT_FORMATS.map((opt) => (

              <option key={opt.value} value={opt.value}>

                {opt.value === 'json' ? t.inventory.exportFormatJson : opt.value === 'xlsx' ? t.inventory.exportFormatXlsx : opt.value === 'csv' ? t.inventory.exportFormatCsv : opt.label}

              </option>

            ))}

          </select>

        </FormField>

        <FormField label={t.inventory.colType}>

          <select className="input" value={filters.type_id} onChange={(e) => onChange({ ...filters, type_id: e.target.value })}>

            <option value="">{t.common.all}</option>

            {(types || []).map((typeOpt) => (

              <option key={typeOpt.id} value={typeOpt.id}>

                {typeOpt.name}

              </option>

            ))}

          </select>

        </FormField>

        <FormField label={t.inventory.exportBusinessService}>

          <select

            className="input"

            value={filters.business_service_id}

            data-testid="inventory-export-business-service"

            onChange={(e) => onChange({ ...filters, business_service_id: e.target.value })}

          >

            <option value="">{t.common.all}</option>

            {(businessServices || []).map((bs) => (

              <option key={bs.id} value={bs.id}>

                {bs.name}

              </option>

            ))}

          </select>

        </FormField>

        <FormField label={t.inventory.exportServiceCode}>

          <input

            className="input"

            value={filters.service_code}

            data-testid="inventory-export-service-code"

            placeholder="PAY-SVC"

            onChange={(e) => onChange({ ...filters, service_code: e.target.value })}

          />

        </FormField>

        <FormField label={t.inventory.colEnvironment} htmlFor="export-env">

          <EnvironmentInput

            id="export-env"

            value={filters.environment}

            onChange={(environment) => onChange({ ...filters, environment })}

            placeholder={t.common.all}

            allowEmpty

          />

        </FormField>

        <FormField label={t.inventory.colOwner}>

          <input className="input" value={filters.owner} onChange={(e) => onChange({ ...filters, owner: e.target.value })} />

        </FormField>

        <FormField label={t.inventory.colCriticality}>

          <select className="input" value={filters.criticality} onChange={(e) => onChange({ ...filters, criticality: e.target.value })}>

            <option value="">{t.common.all}</option>

            {criticalityLevels.map((s) => (

              <option key={s} value={s}>

                {criticalityLabel(t, s)}

              </option>

            ))}

          </select>

        </FormField>

      </div>

      <FormModalActions

        onCancel={onClose}

        onSubmit={() => onExport(format)}

        submitLabel={t.common.export}

        submitTestId="inventory-export-submit"

      />

    </Modal>

  )

}


