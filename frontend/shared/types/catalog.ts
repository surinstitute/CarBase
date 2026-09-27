export interface ApiPage<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface CatalogMake {
  id: string
  name: string
  groupId: string | null
}

export interface CatalogGroup {
  id: string
  name: string
}

export interface CatalogVehicleRecord {
  id: string | number
  variantName?: string | null
  lineage: {
    makeId: string
    modelId: string
    modelYear: number
    [field: string]: unknown
  }
  configuration: {
    bodyStyle?: string
    powertrain?: {
      architecture?: string
      [field: string]: unknown
    } | null
    [field: string]: unknown
  }
  images?: Record<string, { url: string; alt: string }>
  [field: string]: unknown
}

export interface CatalogModel {
  id: string
  makeId: string
  makeName: string
  modelName: string
  year: number
  generation: string | null
  created_at: string
  updated_at: string
  platformId: string | null
  platformName: string | null
  bodyStyles: string[]
  architectures: string[]
  vehicles: CatalogVehicleRecord[]
  image?: {
    url: string
    alt: string
  }
}

export interface CatalogResponse {
  count: number
  groups: CatalogGroup[]
  models: CatalogModel[]
  makes: CatalogMake[]
}