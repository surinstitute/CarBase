<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import type { CatalogResponse } from '#shared/types/catalog'

const filters = useCatalogFiltersStore()
const route = useRoute()

if (typeof route.query.q === 'string') {
  filters.search = route.query.q
}

const { data, status } = useQuery({
  key: ['catalog'],
  query: () => $fetch<CatalogResponse>('/api/catalog')
})

const modelsForMake = computed(() => (data.value?.models ?? []).filter((model) => filters.makeId === 'all' || model.makeId === filters.makeId))
const modelNames = computed(() => [...new Set(modelsForMake.value.map((model) => model.modelName))].sort((first, second) => first.localeCompare(second)))
const years = computed(() => [...new Set(modelsForMake.value
  .filter((model) => filters.modelName === 'all' || model.modelName === filters.modelName)
  .map((model) => model.year))].sort((first, second) => second - first))

watch(() => filters.makeId, () => {
  filters.modelName = 'all'
  filters.year = 'all'
})

watch(() => filters.modelName, () => {
  filters.year = 'all'
})

const filteredModels = computed(() => {
  const term = filters.search.trim().toLocaleLowerCase()
  return (data.value?.models ?? []).filter((model) => {
    const matchesSearch = !term || `${model.makeName} ${model.modelName} ${model.year}`.toLocaleLowerCase().includes(term)
    const matchesMake = filters.makeId === 'all' || model.makeId === filters.makeId
    const matchesModel = filters.modelName === 'all' || model.modelName === filters.modelName
    const matchesYear = filters.year === 'all' || String(model.year) === filters.year
    return matchesSearch && matchesMake && matchesModel && matchesYear
  })
})
</script>

<template>
  <section class="border-b bg-muted/30">
    <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
      <p class="text-sm font-medium text-muted-foreground">Explorar</p>
      <h1 class="text-3xl font-bold tracking-tight">Catálogo de autos</h1>
    </div>
  </section>

  <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Card>
      <CardContent class="grid grid-cols-1 gap-4 p-4 sm:p-6 md:grid-cols-2 xl:grid-cols-[minmax(15rem,1.5fr)_repeat(3,minmax(10rem,1fr))_auto] xl:items-end">
        <label class="grid gap-2 text-sm font-medium">Buscar
          <Input v-model="filters.search" placeholder="Marca, modelo o año" />
        </label>
        <div class="grid gap-2 text-sm font-medium">
          <span>Marca</span>
          <NativeSelect v-model="filters.makeId" class="w-full" aria-label="Filtrar por marca">
            <NativeSelectOption value="all">Todas las marcas</NativeSelectOption>
            <NativeSelectOption v-for="make in data?.makes" :key="make.id" :value="make.id">{{ make.name }}</NativeSelectOption>
          </NativeSelect>
        </div>
        <div class="grid gap-2 text-sm font-medium">
          <span>Modelo</span>
          <NativeSelect v-model="filters.modelName" class="w-full" :disabled="!modelNames.length" aria-label="Filtrar por modelo">
            <NativeSelectOption value="all">Todos los modelos</NativeSelectOption>
            <NativeSelectOption v-for="model in modelNames" :key="model" :value="model">{{ model }}</NativeSelectOption>
          </NativeSelect>
        </div>
        <div class="grid gap-2 text-sm font-medium">
          <span>Año</span>
          <NativeSelect v-model="filters.year" class="w-full" :disabled="!years.length" aria-label="Filtrar por año">
            <NativeSelectOption value="all">Todos los años</NativeSelectOption>
            <NativeSelectOption v-for="year in years" :key="year" :value="String(year)">{{ year }}</NativeSelectOption>
          </NativeSelect>
        </div>
        <Button type="button" variant="outline" @click="filters.reset">Limpiar</Button>
      </CardContent>
    </Card>

    <div class="flex items-center justify-between gap-4">
      <h2 class="text-lg font-semibold tracking-tight">Modelos base</h2>
      <Badge variant="secondary">{{ filteredModels.length }} resultados</Badge>
    </div>

    <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">No se pudo cargar el catálogo. Revisa que la API esté disponible.</p>
    <div v-else-if="status === 'pending'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="item in 6" :key="item" class="h-80" />
    </div>
    <div v-else-if="filteredModels.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <CatalogModelCard v-for="model in filteredModels" :key="model.id" :model="model" />
    </div>
    <Card v-else>
      <CardContent class="flex flex-col items-center gap-2 p-8 text-center">
        <Icon name="tabler:car-off" class="size-8 text-muted-foreground" aria-hidden="true" />
        <h3 class="font-semibold">No hay modelos para mostrar</h3>
        <p class="text-sm text-muted-foreground">Prueba a cambiar los filtros o vuelve más tarde.</p>
      </CardContent>
    </Card>
  </section>
</template>