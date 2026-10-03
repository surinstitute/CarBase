import type { CatalogModelCardsResponse } from '#shared/types/catalog'

export default defineEventHandler(async (event): Promise<CatalogModelCardsResponse> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const name of ['q', 'make', 'body_style', 'page']) {
    const value = query[name]
    if (typeof value === 'string' && value.trim()) {
      params.set(name, value.trim())
    }
  }

  return $fetch<CatalogModelCardsResponse>(
    `${apiBase}/model-generations/cards/${params.size ? `?${params}` : ''}`
  )
})
