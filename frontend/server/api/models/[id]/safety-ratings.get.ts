import type { CatalogSafetyRating } from '#shared/types/catalog'

interface ApiModelDetail {
  safetyRatings: CatalogSafetyRating[]
}

export default defineEventHandler(async (event) => {
  const modelId = getRouterParam(event, 'id')

  if (!modelId) {
    throw createError({ statusCode: 400, statusMessage: 'Model ID is required' })
  }

  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const model = await $fetch<ApiModelDetail>(`${apiBase}/models/${encodeURIComponent(modelId)}/`)

  return model.safetyRatings ?? []
})