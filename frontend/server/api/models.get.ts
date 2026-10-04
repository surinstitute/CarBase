import type { CatalogModel } from '#shared/types/catalog'
import { fetchAllPages } from '../utils/django'

interface ApiModel {
  id: string
  modelGenerationId: string
  model: string
  make: string
  makeName: string
  makeSlug: string
  platform: string | null
  platformName: string | null
  generation: string | null
  body_style: string | null
  year: number
  created_at: string
  updated_at: string
  image: CatalogModel['image'] | null
  architectures: string[]
}

export default defineEventHandler(async (event) => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const name of ['q', 'make', 'model', 'year', 'body_style', 'powertrain_type', 'assembly_country']) {
    const value = query[name]
    if (typeof value === 'string' && value.trim()) {
      params.set(name, value.trim())
    }
  }

  const response = await fetchAllPages<ApiModel>(
    `${apiBase}/models/${params.size ? `?${params}` : ''}`
  )

  return {
    ...response,
    results: response.results.map((model): CatalogModel => ({
      id: model.id,
      modelGenerationId: model.modelGenerationId,
      makeId: model.make,
      makeSlug: model.makeSlug,
      makeName: model.makeName,
      modelName: model.model,
      year: model.year,
      generation: model.generation,
      created_at: model.created_at,
      updated_at: model.updated_at,
      platformId: model.platform,
      platformName: model.platformName,
      baseBodyStyle: model.body_style,
      bodyStyles: model.body_style ? [model.body_style] : [],
      architectures: model.architectures,
      vehicles: [],
      image: model.image ?? undefined
    }))
  }
})
