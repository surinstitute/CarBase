<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { ApiPage, CatalogGroup, CatalogMake, CatalogModel } from '#shared/types/catalog'

const route = useRoute()
const groupSlug = computed(() => String(route.params.id))
const { data: groups, status: groupsStatus } = useQuery({
  key: ['groups'],
  query: () => $fetch<ApiPage<CatalogGroup>>('/api/groups')
})
const { data: makes, status: makesStatus } = useQuery({
  key: ['makes'],
  query: () => $fetch<ApiPage<CatalogMake>>('/api/makes')
})
const { data: models, status: modelsStatus } = useQuery({
  key: ['models'],
  query: () => $fetch<ApiPage<CatalogModel>>('/api/models')
})
const status = computed(() => (
  groupsStatus.value === 'error' || makesStatus.value === 'error' || modelsStatus.value === 'error'
    ? 'error'
    : groupsStatus.value === 'pending' || makesStatus.value === 'pending' || modelsStatus.value === 'pending'
      ? 'pending'
      : 'success'
))
const group = computed(() => groups.value?.results.find((item) => item.slug === groupSlug.value))
const groupMakes = computed(() => makes.value?.results.filter((make) => make.groupId === group.value?.id) ?? [])
const groupModels = computed(() => {
  const makeIds = new Set(groupMakes.value.map((make) => make.id))
  return models.value?.results.filter((model) => makeIds.has(model.makeId)) ?? []
})
</script>

<template>
  <section v-if="status === 'pending'" class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Skeleton class="h-8 w-48" />
    <Skeleton class="h-16 w-full" />
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><Skeleton v-for="item in 3" :key="item" class="h-36" /></div>
  </section>
  <section v-else-if="status === 'error'" class="mx-auto w-full max-w-6xl px-4 py-8">
    <p role="alert" class="text-sm text-destructive">No se pudo cargar la información de grupos.</p>
  </section>
  <section v-else-if="group" class="mx-auto w-full max-w-6xl space-y-8 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/groups">Grupos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>{{ group.name }}</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <header class="flex flex-wrap items-end justify-between gap-4 border-b pb-6">
      <div class="space-y-2">
        <p class="text-sm text-muted-foreground">Grupo automotriz</p>
        <h1 class="text-3xl font-bold tracking-tight">{{ group.name }}</h1>
      </div>
      <div class="flex gap-2">
        <Badge variant="secondary">{{ groupMakes.length }} marcas</Badge>
        <Badge variant="outline">{{ groupModels.length }} modelos</Badge>
      </div>
    </header>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Marcas</h2>
      <div v-if="groupMakes.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card v-for="make in groupMakes" :key="make.id" class="transition-shadow hover:shadow-md">
          <CardHeader>
            <div class="flex items-center gap-3">
              <img v-if="make.iconSvg" :src="make.iconSvg" alt="" class="size-10 object-contain">
              <CardTitle><NuxtLink :to="`/makes/${make.slug}`" class="underline underline-offset-4">{{ make.name }}</NuxtLink></CardTitle>
            </div>
            <CardDescription>{{ groupModels.filter((model) => model.makeId === make.id).length }} modelos</CardDescription>
          </CardHeader>
          <CardContent>
            <NuxtLink :to="`/makes/${make.slug}`" class="text-sm font-medium underline underline-offset-4">Ver marca</NuxtLink>
          </CardContent>
        </Card>
      </div>
      <Card v-else>
        <CardContent class="p-6 text-sm text-muted-foreground">Este grupo aún no tiene marcas asociadas.</CardContent>
      </Card>
    </section>

    <section v-if="groupModels.length" class="space-y-3">
      <h2 class="text-xl font-semibold">Modelos</h2>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <CatalogModelCard v-for="model in groupModels" :key="model.id" :model="model" />
      </div>
    </section>
  </section>
  <section v-else class="mx-auto w-full max-w-6xl space-y-4 px-4 py-8">
    <h1>Grupo no encontrado</h1>
    <NuxtLink to="/groups" class="underline underline-offset-4">Volver a grupos</NuxtLink>
  </section>
</template>