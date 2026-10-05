import type { CatalogModel } from '#shared/types/catalog'

export function urlSegment(value: string) {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function modelOverviewPath(model: Pick<CatalogModel, 'makeSlug' | 'modelName'>) {
  return `/makes/${model.makeSlug}/models/${urlSegment(model.modelName)}`
}

export function modelIdPath(modelId: string) {
  return `/models/${encodeURIComponent(modelId)}`
}

export function modelYearPath(model: Pick<CatalogModel, 'makeSlug' | 'modelName' | 'generation' | 'year' | 'baseBodyStyle'>) {
  return `${modelOverviewPath(model)}/${urlSegment(model.generation ?? 'gen')}/${model.year}-${model.baseBodyStyle ?? 'unspecified'}`
}

export function variantPath(model: Pick<CatalogModel, 'makeSlug' | 'modelName' | 'generation' | 'year' | 'baseBodyStyle'>, variantName: string | null | undefined, variantId: string | number) {
  return `${modelYearPath(model)}/${variantName ? urlSegment(variantName) : variantId}`
}

export function vehicleIdPath(modelId: string, vehicleId: string | number) {
  return `${modelIdPath(modelId)}/variant/${encodeURIComponent(String(vehicleId))}`
}
