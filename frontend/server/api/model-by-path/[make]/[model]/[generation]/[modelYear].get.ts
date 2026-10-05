import type {
  CatalogModelDetail,
  CatalogModelImage,
  CatalogSafetyRating,
  CatalogVehicleRecord,
  CatalogWarranty
} from '#shared/types/catalog'

interface ApiModelDetail {
  id: string
  modelGenerationId: string
  model: string
  make: string
  makeName: string
  makeSlug: string
  platform: string | null
  platformName: string | null
  generation: string | null
  year: number
  created_at: string
  updated_at: string
  body_style: string | null
  image: CatalogModelDetail['image'] | null
  images: CatalogModelImage[]
  safetyRatings: CatalogSafetyRating[]
  warranty: CatalogWarranty | null
  variants: CatalogVehicleRecord[]
}

export default defineEventHandler(async (event): Promise<CatalogModelDetail> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const make = getRouterParam(event, 'make')
  const model = getRouterParam(event, 'model')
  const generation = getRouterParam(event, 'generation')
  const modelYear = getRouterParam(event, 'modelYear')

  if (!make || !model || !generation || !modelYear) {
    throw createError({ statusCode: 400, statusMessage: 'Model path is required' })
  }

  const modelDetail = await $fetch<ApiModelDetail>(
    `${apiBase}/models/by-path/${encodeURIComponent(make)}/${encodeURIComponent(model)}/${encodeURIComponent(generation)}/${encodeURIComponent(modelYear)}/`
  )
  const variants = modelDetail.variants ?? []
  const architectures = variants
    .map((variant) => variant.configuration.powertrain?.architecture)
    .filter((architecture): architecture is string => typeof architecture === 'string')
  const variantImage = variants
    .map((variant) => variant.images?.leftSide ?? variant.images?.silhouette ?? variant.images?.front)
    .find((image): image is NonNullable<CatalogModelDetail['image']> => Boolean(image))

  return {
    id: modelDetail.id,
    modelGenerationId: modelDetail.modelGenerationId,
    makeId: modelDetail.make,
    makeSlug: modelDetail.makeSlug,
    makeName: modelDetail.makeName,
    modelName: modelDetail.model,
    year: modelDetail.year,
    generation: modelDetail.generation,
    created_at: modelDetail.created_at,
    updated_at: modelDetail.updated_at,
    platformId: modelDetail.platform,
    platformName: modelDetail.platformName,
    baseBodyStyle: modelDetail.body_style,
    bodyStyles: modelDetail.body_style ? [modelDetail.body_style] : [],
    architectures: [...new Set(architectures)],
    vehicles: variants,
    image: modelDetail.image ?? variantImage,
    images: modelDetail.images ?? [],
    safetyRatings: modelDetail.safetyRatings ?? [],
    warranty: modelDetail.warranty
  }
})
