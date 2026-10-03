<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import type { ApiPage, CatalogModel, CatalogVehicleRecord } from '#shared/types/catalog'

const route = useRoute()
const router = useRouter()
const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const activeSearch = ref(search.value)
const make = ref(typeof route.query.make === 'string' ? route.query.make : 'all')
const group = ref(typeof route.query.group === 'string' ? route.query.group : 'all')
const year = ref(typeof route.query.year === 'string' ? route.query.year : 'all')
const powertrainType = ref(typeof route.query.powertrain_type === 'string' ? route.query.powertrain_type : 'all')
const assemblyCountry = ref(typeof route.query.assembly_country === 'string' ? route.query.assembly_country : 'all')
const safety = ref(typeof route.query.safety === 'string' ? route.query.safety : 'all')
const sort = ref(typeof route.query.sort === 'string' ? route.query.sort : 'newest')
const page = ref(Number.parseInt(typeof route.query.page === 'string' ? route.query.page : '1', 10) || 1)
const query = computed(() => ({
  page: String(page.value),
  ...(activeSearch.value.trim() ? { q: activeSearch.value.trim() } : {}),
  ...(make.value !== 'all' ? { make: make.value } : {}),
  ...(group.value !== 'all' ? { group: group.value } : {}),
  ...(year.value !== 'all' ? { year: year.value } : {}),
  ...(powertrainType.value !== 'all' ? { powertrain_type: powertrainType.value } : {}),
  ...(assemblyCountry.value !== 'all' ? { assembly_country: assemblyCountry.value } : {}),
  ...(safety.value !== 'all' ? { safety: safety.value } : {}),
  ...(sort.value !== 'newest' ? { sort: sort.value } : {})
}))

watch(query, (value) => {
  router.replace({ path: '/vehicles', query: value })
})

const { data, status } = useQuery({
  key: () => ['vehicles', query.value],
  query: () => $fetch<ApiPage<CatalogVehicleRecord>>('/api/vehicles', { query: query.value })
})
const { data: filterOptions } = useQuery({
  key: ['vehicle-filter-options'],
  query: () => $fetch<{
    years: number[]
    powertrainTypes: string[]
    assemblyCountries: Array<{ code: string, name: string }>
    makes: Array<{ id: string, name: string }>
    groups: Array<{ id: string, name: string }>
  }>('/api/vehicles/filter-options')
})

const pageCount = computed(() => Math.max(1, Math.ceil((data.value?.count ?? 0) / 10)))

function submitSearch() {
  activeSearch.value = search.value
  page.value = 1
}

function goToPage(targetPage: number) {
  page.value = targetPage
}

function resetFilters() {
  search.value = ''
  activeSearch.value = ''
  make.value = 'all'
  group.value = 'all'
  year.value = 'all'
  powertrainType.value = 'all'
  assemblyCountry.value = 'all'
  safety.value = 'all'
  sort.value = 'newest'
  page.value = 1
}

function modelContext(vehicle: CatalogVehicleRecord): Pick<CatalogModel, 'id' | 'makeId' | 'makeName' | 'modelName' | 'image'> {
  const image = vehicle.images?.leftSide ?? vehicle.images?.silhouette ?? vehicle.images?.front
  return {
    id: vehicle.lineage.modelId,
    makeId: vehicle.lineage.makeId,
    makeName: vehicle.lineage.makeName ?? '',
    modelName: vehicle.lineage.modelName ?? '',
    ...(image ? { image } : {})
  }
}
</script>

<template>
  <div>
    <section class="border-b bg-muted/30">
      <div class="mx-auto grid w-full max-w-6xl gap-8 px-4 py-12 sm:py-16 lg:grid-cols-[1fr_minmax(20rem,0.8fr)] lg:items-end">
        <div class="space-y-3">
          <p class="text-sm font-medium text-muted-foreground">Explorar vehículos</p>
          <h1 class="max-w-2xl text-3xl font-bold tracking-tight sm:text-4xl">Busca entre todas las versiones</h1>
          <p class="max-w-xl text-muted-foreground">Cada variante, con su propia configuración y ficha.</p>
        </div>
        <form class="flex gap-2" role="search" @submit.prevent="submitSearch">
          <label for="vehicles-search" class="sr-only">Buscar marca, modelo o versión</label>
          <Input id="vehicles-search" v-model="search" placeholder="Marca, modelo o versión" class="min-w-0 flex-1 bg-background" />
          <Button type="submit" aria-label="Buscar vehículos">
            <Icon name="tabler:search" class="size-4" aria-hidden="true" />
            <span class="hidden sm:inline">Buscar</span>
          </Button>
        </form>
      </div>
    </section>

    <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
      <Card>
        <CardContent class="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 sm:p-6 xl:grid-cols-4 xl:items-end">
          <label class="grid gap-2 text-sm font-medium">Marca
            <NativeSelect v-model="make" class="w-full" :disabled="!filterOptions?.makes.length" aria-label="Filtrar vehículos por marca">
              <NativeSelectOption value="all">Todas las marcas</NativeSelectOption>
              <NativeSelectOption v-for="option in filterOptions?.makes" :key="option.id" :value="option.id">{{ option.name }}</NativeSelectOption>
            </NativeSelect>
          </label>
          <label class="grid gap-2 text-sm font-medium">Grupo
            <NativeSelect v-model="group" class="w-full" :disabled="!filterOptions?.groups.length" aria-label="Filtrar vehículos por grupo">
              <NativeSelectOption value="all">Todos los grupos</NativeSelectOption>
              <NativeSelectOption v-for="option in filterOptions?.groups" :key="option.id" :value="option.id">{{ option.name }}</NativeSelectOption>
            </NativeSelect>
          </label>
          <label class="grid gap-2 text-sm font-medium">Año
            <NativeSelect v-model="year" class="w-full" :disabled="!filterOptions?.years.length" aria-label="Filtrar vehículos por año">
              <NativeSelectOption value="all">Todos los años</NativeSelectOption>
              <NativeSelectOption v-for="option in filterOptions?.years" :key="option" :value="String(option)">{{ option }}</NativeSelectOption>
            </NativeSelect>
          </label>
          <label class="grid gap-2 text-sm font-medium">Propulsión
            <NativeSelect v-model="powertrainType" class="w-full" :disabled="!filterOptions?.powertrainTypes.length" aria-label="Filtrar vehículos por propulsión">
              <NativeSelectOption value="all">Todas las propulsiones</NativeSelectOption>
              <NativeSelectOption v-for="option in filterOptions?.powertrainTypes" :key="option" :value="option">{{ option.replaceAll('_', ' ') }}</NativeSelectOption>
            </NativeSelect>
          </label>
          <label class="grid gap-2 text-sm font-medium">País de armado
            <NativeSelect v-model="assemblyCountry" class="w-full" :disabled="!filterOptions?.assemblyCountries.length" aria-label="Filtrar vehículos por país de armado">
              <NativeSelectOption value="all">Todos los países</NativeSelectOption>
              <NativeSelectOption v-for="country in filterOptions?.assemblyCountries" :key="country.code" :value="country.code">{{ country.name }}</NativeSelectOption>
            </NativeSelect>
          </label>
          <label class="grid gap-2 text-sm font-medium">Seguridad
            <NativeSelect v-model="safety" class="w-full" aria-label="Filtrar vehículos por seguridad">
              <NativeSelectOption value="all">Todos los vehículos</NativeSelectOption>
              <NativeSelectOption value="true">Con paquete de seguridad</NativeSelectOption>
              <NativeSelectOption value="false">Sin paquete de seguridad</NativeSelectOption>
            </NativeSelect>
          </label>
          <label class="grid gap-2 text-sm font-medium">Ordenar por
            <NativeSelect v-model="sort" class="w-full" aria-label="Ordenar vehículos">
              <NativeSelectOption value="newest">Año: más reciente</NativeSelectOption>
              <NativeSelectOption value="az">A-Z</NativeSelectOption>
              <NativeSelectOption value="price_asc">Precio: menor a mayor</NativeSelectOption>
              <NativeSelectOption value="price_desc">Precio: mayor a menor</NativeSelectOption>
            </NativeSelect>
          </label>
          <Button type="button" variant="outline" @click="resetFilters">Limpiar</Button>
        </CardContent>
      </Card>

      <div class="flex items-center justify-between gap-4">
        <h2 class="text-lg font-semibold">Vehículos</h2>
        <Badge variant="secondary">{{ data?.count ?? 0 }} resultados</Badge>
      </div>

      <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">No se pudieron cargar los vehículos. Revisa que la API esté disponible.</p>
      <div v-else-if="status === 'pending'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Skeleton v-for="item in 6" :key="item" class="h-80" />
      </div>
      <div v-else-if="data?.results.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <CatalogVehicleCard v-for="(vehicle, index) in data.results" :key="vehicle.id" :model="modelContext(vehicle)" :vehicle="vehicle" :index="index" />
      </div>
      <Card v-else>
        <CardContent class="flex flex-col items-center gap-2 p-8 text-center">
          <Icon name="tabler:car-off" class="size-8 text-muted-foreground" aria-hidden="true" />
          <h3 class="font-semibold">No hay vehículos para mostrar</h3>
          <p class="text-sm text-muted-foreground">Prueba otra búsqueda o vuelve más tarde.</p>
        </CardContent>
      </Card>

      <nav v-if="pageCount > 1" class="flex items-center justify-center gap-3" aria-label="Paginación de vehículos">
        <Button type="button" variant="outline" size="icon" :disabled="page <= 1" aria-label="Página anterior" title="Página anterior" @click="goToPage(page - 1)">
          <Icon name="tabler:chevron-left" class="size-4" aria-hidden="true" />
        </Button>
        <span class="text-sm text-muted-foreground">Página {{ page }} de {{ pageCount }}</span>
        <Button type="button" variant="outline" size="icon" :disabled="page >= pageCount" aria-label="Página siguiente" title="Página siguiente" @click="goToPage(page + 1)">
          <Icon name="tabler:chevron-right" class="size-4" aria-hidden="true" />
        </Button>
      </nav>
    </section>
  </div>
</template>