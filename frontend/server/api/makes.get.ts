import type { CatalogMake } from '#shared/types/catalog'
import { fetchAllPages } from '../utils/django'

interface ApiMake {
  makeId: string
  name: string
  slug: string
  description: string
  country: string | null
  group: string | null
  icon_svg: string | null
  website: string
  phone: string
  legal_representative: string
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
      description: make.description,
      country: make.country,
      groupId: make.group,
      iconSvg: make.icon_svg,
      website: make.website,
      phone: make.phone,
      legalRepresentative: make.legal_representative,
      modelGenerationCount: make.modelGenerationCount,
      modelYearCount: make.modelYearCount,
      vehicleCount: make.vehicleCount
    }))
  }
})
