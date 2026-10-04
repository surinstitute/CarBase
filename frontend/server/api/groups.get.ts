import type { CatalogGroup } from '#shared/types/catalog'
import { fetchAllPages } from '../utils/django'

interface ApiGroup {
  groupId: string
  name: string
  slug: string
}

export default defineEventHandler(async (event) => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const response = await fetchAllPages<ApiGroup>(`${apiBase}/groups/`)

  return {
    ...response,
    results: response.results.map((group): CatalogGroup => ({
      id: group.groupId,
      name: group.name,
      slug: group.slug
    }))
  }
})
