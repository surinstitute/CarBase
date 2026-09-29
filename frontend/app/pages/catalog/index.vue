<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useQuery } from '@pinia/colada'
import { refDebounced } from '@vueuse/core'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import type { CatalogResponse } from '#shared/types/catalog'

const filters = useCatalogFiltersStore()
const { search } = storeToRefs(filters)
const route = useRoute()
const router = useRouter()

function queryValue(name: string) {
  const value = route.query[name]
  return typeof value === 'string' ? value : ''
}

filters.search = queryValue('q')
filters.makeId = queryValue('make') || 'all'
filters.year = queryValue('year') || 'all'
filters.bodyStyle = queryValue('body_style') || 'all'
filters.powertrainType = queryValue('powertrain_type') || 'all'
filters.assemblyCountry = queryValue('assembly_country') || 'all'

const requestedPage = Number.parseInt(queryValue('page'), 10)
const page = ref(Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1)
const debouncedSearch = refDebounced(search, 300)
const catalogQuery = computed(() => ({
  page: String(page.value),
  ...(debouncedSearch.value.trim() ? { q: debouncedSearch.value.trim() } : {}),
  ...(filters.makeId !== 'all' ? { make: filters.makeId } : {}),
  ...(filters.year !== 'all' ? { year: filters.year } : {}),
  ...(filters.bodyStyle !== 'all' ? { body_style: filters.bodyStyle } : {}),
  ...(filters.powertrainType !== 'all' ? { powertrain_type: filters.powertrainType } : {}),
  ...(filters.assemblyCountry !== 'all' ? { assembly_country: filters.assemblyCountry } : {})
}))

const { data, status } = useQuery({
  key: () => ['catalog', catalogQuery.value],
  query: () => $fetch<CatalogResponse>('/api/catalog', { query: catalogQuery.value })
})

watch(catalogQuery, (query) => {
  if (JSON.stringify(route.query) !== JSON.stringify(query)) {
    router.replace({ query })
  }
})

const years = computed(() => data.value?.filterOptions.years ?? [])
const bodyStyles = computed(() => data.value?.filterOptions.bodyStyles ?? [])
const powertrainTypes = computed(() => data.value?.filterOptions.powertrainTypes ?? [])
const assemblyCountries = computed(() => data.value?.filterOptions.assemblyCountries ?? [])
const pageCount = computed(() => Math.max(1, Math.ceil((data.value?.count ?? 0) / 10)))

watch(() => filters.makeId, () => {
  filters.year = 'all'
  page.value = 1
})

watch([() => debouncedSearch.value, () => filters.year, () => filters.assemblyCountry], () => {
  page.value = 1
})

watch([() => filters.bodyStyle, () => filters.powertrainType], () => {
  page.value = 1
})

function resetFilters() {
  filters.reset()
  page.value = 1
}

function bodyStyleLabel(bodyStyle: string) {
  const labels: Record<string, string> = {
    sedan: 'Sedán', hatchback: 'Hatchback', fastback: 'Fastback', coupe: 'Coupé', convertible: 'Convertible', wagon: 'Familiar', suv: 'SUV', crossover: 'Crossover', pickup: 'Pickup', van: 'Van', minivan: 'Minivan', liftback: 'Liftback', roadster: 'Roadster', targa: 'Targa', other: 'Otro'
  }
  return labels[bodyStyle] ?? bodyStyle
}

function powertrainTypeLabel(powertrainType: string) {
  const labels: Record<string, string> = { combustion: 'Combustión', hybrid: 'Híbrido', electric: 'Eléctrico' }
  return labels[powertrainType] ?? powertrainType
}
</script>

<template>
  <div>
    <section class="border-b bg-muted/30">
      <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
        <p class="text-sm font-medium text-muted-foreground">Explorar</p>
        <h1 class="text-3xl font-bold tracking-tight">Catálogo de autos</h1>
      </div>
    </section>

    <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
      <Card>
        <CardContent class="grid grid-cols-1 gap-4 p-4 sm:p-6 md:grid-cols-2 xl:grid-cols-4 xl:items-end">
          <label class="grid gap-2 text-sm font-medium">Buscar
            <Input v-model="filters.search" placeholder="Modelo o generación" />
          </label>
          <div class="grid gap-2 text-sm font-medium">
            <span>Marca</span>
            <NativeSelect v-model="filters.makeId" class="w-full" aria-label="Filtrar por marca">
              <NativeSelectOption value="all">Todas las marcas</NativeSelectOption>
              <NativeSelectOption v-for="make in data?.makes" :key="make.id" :value="make.id">{{ make.name }}</NativeSelectOption>
            </NativeSelect>
          </div>
          <div class="grid gap-2 text-sm font-medium">
            <span>Año</span>
            <NativeSelect v-model="filters.year" class="w-full" :disabled="!years.length" aria-label="Filtrar por año">
              <NativeSelectOption value="all">Todos los años</NativeSelectOption>
              <NativeSelectOption v-for="year in years" :key="year" :value="String(year)">{{ year }}</NativeSelectOption>
            </NativeSelect>
          </div>
          <div class="grid gap-2 text-sm font-medium">
            <span>Carrocería</span>
            <NativeSelect v-model="filters.bodyStyle" class="w-full" :disabled="!bodyStyles.length" aria-label="Filtrar por carrocería">
              <NativeSelectOption value="all">Todas las carrocerías</NativeSelectOption>
              <NativeSelectOption v-for="bodyStyle in bodyStyles" :key="bodyStyle" :value="bodyStyle">{{ bodyStyleLabel(bodyStyle) }}</NativeSelectOption>
            </NativeSelect>
          </div>
          <div class="grid gap-2 text-sm font-medium">
            <span>Propulsión</span>
            <NativeSelect v-model="filters.powertrainType" class="w-full" :disabled="!powertrainTypes.length" aria-label="Filtrar por tipo de propulsión">
              <NativeSelectOption value="all">Todas las propulsiones</NativeSelectOption>
              <NativeSelectOption v-for="powertrainType in powertrainTypes" :key="powertrainType" :value="powertrainType">{{ powertrainTypeLabel(powertrainType) }}</NativeSelectOption>
            </NativeSelect>
          </div>
          <div class="grid gap-2 text-sm font-medium">
            <span>País de armado</span>
            <NativeSelect v-model="filters.assemblyCountry" class="w-full" :disabled="!assemblyCountries.length" aria-label="Filtrar por país de armado">
              <NativeSelectOption value="all">Todos los países</NativeSelectOption>
              <NativeSelectOption v-for="country in assemblyCountries" :key="country.code" :value="country.code">{{ country.name }}</NativeSelectOption>
            </NativeSelect>
          </div>
          <Button type="button" variant="outline" @click="resetFilters">Limpiar</Button>
        </CardContent>
      </Card>

    <div class="flex items-center justify-between gap-4">
      <h2 class="text-lg font-semibold tracking-tight">Modelos base</h2>
      <Badge variant="secondary">{{ data?.count ?? 0 }} resultados</Badge>
    </div>

    <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">No se pudo cargar el catálogo. Revisa que la API esté disponible.</p>
    <div v-else-if="status === 'pending'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="item in 6" :key="item" class="h-80" />
    </div>
    <div v-else-if="data?.models.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <CatalogModelCard v-for="model in data.models" :key="model.id" :model="model" />
    </div>
    <Card v-else>
      <CardContent class="flex flex-col items-center gap-2 p-8 text-center">
        <Icon name="tabler:car-off" class="size-8 text-muted-foreground" aria-hidden="true" />
        <h3 class="font-semibold">No hay modelos para mostrar</h3>
        <p class="text-sm text-muted-foreground">Prueba a cambiar los filtros o vuelve más tarde.</p>
      </CardContent>
    </Card>

      <nav v-if="pageCount > 1" class="flex items-center justify-center gap-3" aria-label="Paginación">
        <Button type="button" variant="outline" size="icon" :disabled="!data?.previous" aria-label="Página anterior" title="Página anterior" @click="page--">
          <Icon name="tabler:chevron-left" class="size-4" aria-hidden="true" />
        </Button>
        <span class="text-sm text-muted-foreground">Página {{ page }} de {{ pageCount }}</span>
        <Button type="button" variant="outline" size="icon" :disabled="!data?.next" aria-label="Página siguiente" title="Página siguiente" @click="page++">
          <Icon name="tabler:chevron-right" class="size-4" aria-hidden="true" />
        </Button>
      </nav>
    </section>
  </div>
</template>