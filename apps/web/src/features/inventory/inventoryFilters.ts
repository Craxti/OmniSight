export type InventoryFilterState = {
  q: string
  type_id: string
  status: string
  environment: string
  owner: string
  hostname: string
  external_id: string
}

export const defaultInventoryFilters: InventoryFilterState = {
  q: '',
  type_id: '',
  status: '',
  environment: '',
  owner: '',
  hostname: '',
  external_id: '',
}
