import type { CatalogVehicleRecord } from '#shared/types/catalog'

export default defineEventHandler(async (event): Promise<CatalogVehicleRecord> => {
  const vehicleId = getRouterParam(event, 'id')
  if (!vehicleId) {
    throw createError({ statusCode: 400, statusMessage: 'Vehicle ID is required' })
  }

  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  return $fetch<CatalogVehicleRecord>(
    `${apiBase}/vehicles/${encodeURIComponent(vehicleId)}/`
  )
})
