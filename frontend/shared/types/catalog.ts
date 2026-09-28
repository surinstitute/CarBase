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
  priceAmount?: string | null
  priceCurrency?: string
  monthlySales?: Array<{
    month: number
    year: number
    unitsSold: number
  }>
  recalls?: Array<{
    authority: string
    recallNumber: string
    country: string | null
    title: string
    description: string
    risk: string
    riskConsequence: string
    countermeasure: string
    actions: string
    status: 'open' | 'resolved'
    publishedDate: string | null
    remedy: string
    sourceUrl: string
  }>
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
  next: string | null
  previous: string | null
  filterOptions: {
    models: string[]
    years: number[]
    assemblyCountries: Array<{
      code: string
      name: string
    }>
  }
  groups: CatalogGroup[]
  models: CatalogModel[]
  makes: CatalogMake[]
}