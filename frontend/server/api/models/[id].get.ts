import type {
  CatalogModelDetail,
  CatalogModelImage,
  CatalogSafetyRating,
  CatalogVehicleRecord,
  CatalogWarranty
} from '#shared/types/catalog'

interface ApiModelDetail {
  id: string
  model: string
  make: string
  makeName: string
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
  const modelId = getRouterParam(event, 'id')

  if (!modelId) {
    throw createError({ statusCode: 400, statusMessage: 'Model ID is required' })
  }

  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const model = await $fetch<ApiModelDetail>(
    `${apiBase}/models/${encodeURIComponent(modelId)}/`
  )
  const variants = model.variants ?? []
  const architectures = variants
    .map((variant) => variant.configuration.powertrain?.architecture)
    .filter((architecture): architecture is string => typeof architecture === 'string')
  const variantImage = variants
    .map((variant) => variant.images?.leftSide ?? variant.images?.silhouette ?? variant.images?.front)
    .find((image): image is NonNullable<CatalogModelDetail['image']> => Boolean(image))

  return {
    id: model.id,
    makeId: model.make,
    makeName: model.makeName,
    modelName: model.model,
    year: model.year,
    generation: model.generation,
    created_at: model.created_at,
    updated_at: model.updated_at,
    platformId: model.platform,
    platformName: model.platformName,
    bodyStyles: model.body_style ? [model.body_style] : [],
    architectures: [...new Set(architectures)],
    vehicles: variants,
    image: model.image ?? variantImage,
    images: model.images ?? [],
    safetyRatings: model.safetyRatings ?? [],
    warranty: model.warranty
  }
})