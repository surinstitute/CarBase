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
  const [vehiclesPage, makesPage, modelsPage, platformsPage, groupsPage] = await Promise.all([
    fetchAll<CatalogVehicleRecord>(`${apiBase}/vehicles/`),
    fetchAll<ApiMake>(`${apiBase}/makes/`),
    fetchAll<ApiModel>(`${apiBase}/models/`),
    fetchAll<ApiPlatform>(`${apiBase}/platforms/`),
    fetchAll<ApiGroup>(`${apiBase}/groups/`)
  ])

  const makesById = new Map(makesPage.results.map((make) => [make.makeId, make.name]))
  const platformsById = new Map(platformsPage.results.map((platform) => [platform.platformId, platform.name]))
  const detailsByModelId = new Map<string, {
    bodyStyles: Set<string>
    architectures: Set<string>
    image?: CatalogModel['image']
    vehicles: CatalogVehicleRecord[]
  }>()

  for (const vehicle of vehiclesPage.results) {
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

  return { count: modelsPage.count, groups, models, makes }
})