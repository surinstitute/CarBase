interface VehicleFilterOptions {
  years: number[]
  powertrainTypes: Array<'combustion' | 'hybrid' | 'plug_in_hybrid' | 'electric'>
  assemblyCountries: Array<{ code: string, name: string }>
  makes: Array<{ id: string, name: string }>
  groups: Array<{ id: string, name: string }>
}

export default defineEventHandler(async (event): Promise<VehicleFilterOptions> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, '')
  return await $fetch<VehicleFilterOptions>(`${apiBase}/vehicles/filter-options/`)
})