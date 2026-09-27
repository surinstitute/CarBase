import type { ApiPage, CatalogMake, CatalogModel, CatalogResponse, CatalogVehicleRecord } from '#shared/types/catalog'

interface ApiMake {
  makeId: string
  name: string
  group: string | null
}

interface ApiGroup {
  groupId: string
  name: string
}

interface ApiModel {
  id: string
  model: string
  make: string
  platform: string | null
  generation: string | null
  year: number
  created_at: string
  updated_at: string
}

interface ApiPlatform {
  platformId: string
  name: string
}

async function fetchAll<T>(url: string) {
  const firstPage = await $fetch<ApiPage<T>>(url)
  const results = [...firstPage.results]
  let nextPage = firstPage.next

  while (nextPage) {
    const page = await $fetch<ApiPage<T>>(nextPage)
    results.push(...page.results)
    nextPage = page.next
  }

  return { count: firstPage.count, results }
}

export default defineEventHandler(async (event): Promise<CatalogResponse> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  const query = getQuery(event)
  const modelParams = new URLSearchParams()
  const filterParams = new URLSearchParams()

  for (const name of ['q', 'make', 'model', 'year', 'assembly_country', 'page']) {
    const value = query[name]
    if (typeof value === 'string' && value.trim()) {
      modelParams.set(name, value.trim())
    }
  }

  for (const name of ['make', 'model', 'assembly_country']) {
    const value = query[name]
    if (typeof value === 'string' && value.trim()) {
      filterParams.set(name, value.trim())
    }
  }

  const modelsUrl = `${apiBase}/models/${modelParams.size ? `?${modelParams}` : ''}`
  const filterOptionsUrl = `${apiBase}/models/filter-options/${filterParams.size ? `?${filterParams}` : ''}`
  const paginatedModels = typeof query.page === 'string'
  const [makesPage, modelsPage, platformsPage, groupsPage, filterOptions] = await Promise.all([
    fetchAll<ApiMake>(`${apiBase}/makes/`),
    paginatedModels
      ? $fetch<ApiPage<ApiModel>>(modelsUrl)
      : fetchAll<ApiModel>(modelsUrl),
    fetchAll<ApiPlatform>(`${apiBase}/platforms/`),
    fetchAll<ApiGroup>(`${apiBase}/groups/`),
    $fetch<CatalogResponse['filterOptions']>(filterOptionsUrl)
  ])
  const vehiclePages = await Promise.all(
    modelsPage.results.map((model) => fetchAll<CatalogVehicleRecord>(
      `${apiBase}/vehicles/?model=${encodeURIComponent(model.id)}`
    ))
  )

  const makesById = new Map(makesPage.results.map((make) => [make.makeId, make.name]))
  const platformsById = new Map(platformsPage.results.map((platform) => [platform.platformId, platform.name]))
  const detailsByModelId = new Map<string, {
    bodyStyles: Set<string>
    architectures: Set<string>
    image?: CatalogModel['image']
    vehicles: CatalogVehicleRecord[]
  }>()

  for (const vehicle of vehiclePages.flatMap((vehiclePage) => vehiclePage.results)) {
    const details = detailsByModelId.get(vehicle.lineage.modelId) ?? {
      bodyStyles: new Set<string>(),
      architectures: new Set<string>(),
      vehicles: []
    }
    const image = vehicle.images?.leftSide ?? vehicle.images?.silhouette ?? vehicle.images?.front

    if (vehicle.configuration.bodyStyle) {
      details.bodyStyles.add(vehicle.configuration.bodyStyle)
    }
    if (vehicle.configuration.powertrain?.architecture) {
      details.architectures.add(vehicle.configuration.powertrain.architecture)
    }
    details.image ??= image
    details.vehicles.push(vehicle)
    detailsByModelId.set(vehicle.lineage.modelId, details)
  }

  const models: CatalogModel[] = modelsPage.results.map((model) => {
    const details = detailsByModelId.get(model.id)

    return {
      id: model.id,
      makeId: model.make,
      makeName: makesById.get(model.make) ?? 'Marca sin nombre',
      modelName: model.model,
      year: model.year,
      generation: model.generation,
      created_at: model.created_at,
      updated_at: model.updated_at,
      platformId: model.platform,
      platformName: model.platform ? platformsById.get(model.platform) ?? null : null,
      bodyStyles: [...(details?.bodyStyles ?? [])],
      architectures: [...(details?.architectures ?? [])],
      vehicles: details?.vehicles ?? [],
      image: details?.image
    }
  })

  const makes: CatalogMake[] = makesPage.results.map(({ makeId, name }) => ({
    id: makeId,
    name,
    groupId: makesPage.results.find((make) => make.makeId === makeId)?.group ?? null
  }))

  const groups = groupsPage.results.map(({ groupId, name }) => ({ id: groupId, name }))

  return {
    count: modelsPage.count,
    next: 'next' in modelsPage ? modelsPage.next : null,
    previous: 'previous' in modelsPage ? modelsPage.previous : null,
    filterOptions,
    groups,
    models,
    makes
  }
})