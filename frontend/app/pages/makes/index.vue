<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import type { CatalogResponse } from '#shared/types/catalog'

const search = ref('')
const { data, status } = useQuery({
  key: ['catalog'],
  query: () => $fetch<CatalogResponse>('/api/catalog')
})
const filteredMakes = computed(() => {
  const term = search.value.trim().toLocaleLowerCase()
  return (data.value?.makes ?? [])
    .filter((make) => make.name.toLocaleLowerCase().includes(term))
    .sort((first, second) => first.name.localeCompare(second.name))
})

function modelCount(makeId: string) {
  return data.value?.models.filter((model) => model.makeId === makeId).length ?? 0
}
</script>

<template>
  <section class="border-b bg-muted/30">
    <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
      <p class="text-sm font-medium text-muted-foreground">Explorar</p>
      <h1 class="text-3xl font-bold tracking-tight">Marcas</h1>
    </div>
  </section>

  <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>Marcas</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <label class="grid w-full gap-2 text-sm font-medium sm:max-w-sm">
        Buscar marca
        <Input v-model="search" placeholder="Nombre de marca" />
      </label>
    </div>

    <div class="flex items-center justify-between gap-4">
      <h2 class="text-lg font-semibold">Todas las marcas</h2>
      <Badge variant="secondary">{{ filteredMakes.length }} marcas</Badge>
    </div>

    <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">No se pudo cargar la lista de marcas.</p>
    <div v-else-if="status === 'pending'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="item in 6" :key="item" class="h-36" />
    </div>
    <div v-else-if="filteredMakes.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card v-for="make in filteredMakes" :key="make.id" class="transition-shadow hover:shadow-md">
        <CardHeader>
          <CardTitle><NuxtLink :to="`/makes/${make.id}`" class="hover:underline underline-offset-4">{{ make.name }}</NuxtLink></CardTitle>
          <CardDescription>{{ modelCount(make.id) }} modelos</CardDescription>
        </CardHeader>
        <CardContent>
          <NuxtLink :to="`/makes/${make.id}`" class="text-sm font-medium underline underline-offset-4">Ver modelos</NuxtLink>
        </CardContent>
      </Card>
    </div>
    <Card v-else>
      <CardContent class="p-6 text-sm text-muted-foreground">No se encontraron marcas.</CardContent>
    </Card>
  </section>
</template>