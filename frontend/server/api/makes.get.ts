import type { CatalogMake } from '#shared/types/catalog'
import { fetchAllPages } from '../utils/django'

interface ApiMake {
  makeId: string
  name: string
  slug: string
  country: string | null
  group: string | null
  modelGenerationCount: number
  modelYearCount: number
  vehicleCount: number
}

export default defineEventHandler(async (event) => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const response = await fetchAllPages<ApiMake>(`${apiBase}/makes/`)

  return {
    ...response,
    results: response.results.map((make): CatalogMake => ({
      id: make.makeId,
      name: make.name,
      slug: make.slug,
      country: make.country,
      groupId: make.group,
      modelGenerationCount: make.modelGenerationCount,
      modelYearCount: make.modelYearCount,
      vehicleCount: make.vehicleCount
    }))
  }
})
