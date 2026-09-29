import type { ApiPage, CatalogRecall } from '#shared/types/catalog'

export default defineEventHandler((event): Promise<ApiPage<CatalogRecall>> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const name of ['q', 'page']) {
    const value = query[name]
    if (typeof value === 'string' && value.trim()) {
      params.set(name, value.trim())
    }
  }

  return $fetch<ApiPage<CatalogRecall>>(`${apiBase}/recalls/?${params}`)
})