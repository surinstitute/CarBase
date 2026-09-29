<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import type { ApiPage, CatalogModel, CatalogVehicleRecord } from '#shared/types/catalog'

const route = useRoute()
const router = useRouter()
const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const page = computed(() => {
  const requestedPage = Number.parseInt(typeof route.query.page === 'string' ? route.query.page : '1', 10)
  return Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1
})
const query = computed(() => ({
  page: String(page.value),
  ...(typeof route.query.q === 'string' && route.query.q.trim() ? { q: route.query.q.trim() } : {})
}))

watch(() => route.query.q, (value) => {
  search.value = typeof value === 'string' ? value : ''
})

const { data, status } = useQuery({
  key: () => ['vehicles', query.value],
  query: () => $fetch<ApiPage<CatalogVehicleRecord>>('/api/vehicles', { query: query.value })
})

const pageCount = computed(() => Math.max(1, Math.ceil((data.value?.count ?? 0) / 10)))

function submitSearch() {
  const value = search.value.trim()
  router.push({ path: '/search', query: value ? { q: value } : undefined })
}

function goToPage(targetPage: number) {
  router.push({
    path: '/search',
    query: {
      ...(typeof route.query.q === 'string' && route.query.q.trim() ? { q: route.query.q.trim() } : {}),
      page: String(targetPage)
    }
  })
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