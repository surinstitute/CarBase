import type { ApiPage, CatalogVehicleRecord } from '#shared/types/catalog'

export default defineEventHandler(async (event): Promise<ApiPage<CatalogVehicleRecord>> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const query = getQuery(event)
  const params = new URLSearchParams()

  for (const name of ['q', 'page']) {
    const value = query[name]
    if (typeof value === 'string' && value.trim()) {
      params.set(name, value.trim())
    }
  }

  const search = params.size ? `?${params}` : ''
  return await $fetch<ApiPage<CatalogVehicleRecord>>(`${apiBase}/vehicles/${search}`)
})