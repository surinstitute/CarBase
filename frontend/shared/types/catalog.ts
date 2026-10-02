export interface ApiPage<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface CatalogMake {
  id: string
  name: string
  slug: string
  country?: string | null
  groupId: string | null
}

export interface CatalogGroup {
  id: string
  name: string
  slug: string
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
    makeName?: string
    modelName?: string
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
  safety?: {
    collisionWarnings?: Partial<Record<'fcw' | 'ldw' | 'bsw' | 'rctw', boolean>>
    collisionIntervention?: Partial<Record<'aebCity' | 'aebPedestrian' | 'aebHighway' | 'aebRear', boolean>>
    drivingControlAssistance?: Partial<Record<'lka' | 'lca' | 'acc' | 'activeDrivingAssistanceDirectDriverMonitoring', boolean>>
    rearSeatSafety?: Partial<Record<'childSafety' | 'rearOccupantAlertEndOfTripReminder', boolean>>
    visibilityAndControl?: Partial<Record<'drl' | 'rearViewCamera' | 'esc' | 'tractionControl' | 'abs', boolean>>
    restraints?: Partial<Record<'airbagSideFront' | 'airbagSideRear' | 'headProtectionAirbag', number>>
  } | null
  images?: Record<string, { url: string; alt: string }>
  [field: string]: unknown
}

export interface CatalogSafetyRating {
  program: 'latin_ncap' | 'euro_ncap' | 'other'
  assessmentYear: number
  overallStars: number
  adultOccupantProtection: number
  childOccupantProtection: number
  vulnerableRoadUserProtection: number
  safetyAssist: number
  sourceUrl: string | null
}

export interface CatalogRecall {
  id: number
  makerId: string
  makerName: string
  recallNumber: string
  title: string
  description: string
  risk: string
  riskConsequence: string
  countermeasure: string
  actions: string
  status: 'open' | 'resolved'
  publishedDate: string | null
  totalUnitsAffected: number | null
  sourceUrl: string
  damageReport: string
  affectedModels: Array<{
    id: string
    name: string
    year: number
  }>
}

export interface CatalogModel {
  id: string
  makeId: string
  makeSlug: string
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

export interface CatalogModelImage {
  view?: 'left_side' | 'right_side' | 'front' | 'rear' | 'silhouette'
  url: string
  alt: string
}

export interface CatalogWarrantyCoverage {
  years: number | null
  kilometers: number | null
  kilometersUnlimited: boolean
}

export interface CatalogWarranty {
  basic?: CatalogWarrantyCoverage
  drivetrain?: CatalogWarrantyCoverage
  corrosion?: CatalogWarrantyCoverage
}

export interface CatalogModelDetail extends CatalogModel {
  safetyRatings: CatalogSafetyRating[]
  images: CatalogModelImage[]
  warranty: CatalogWarranty | null
}

export interface CatalogResponse {
  count: number
  next: string | null
  previous: string | null
  filterOptions: {
    models: string[]
    years: number[]
    bodyStyles: string[]
    powertrainTypes: Array<'combustion' | 'hybrid' | 'plug_in_hybrid' | 'electric'>
    assemblyCountries: Array<{
      code: string
      name: string
    }>
  }
  groups: CatalogGroup[]
  models: CatalogModel[]
  makes: CatalogMake[]
}