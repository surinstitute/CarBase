<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { CatalogResponse } from '#shared/types/catalog'

const route = useRoute()
const groupId = computed(() => String(route.params.id))
const { data, status } = useQuery({
  key: ['catalog'],
  query: () => $fetch<CatalogResponse>('/api/catalog')
})
const group = computed(() => data.value?.groups.find((item) => item.id === groupId.value))
const makes = computed(() => data.value?.makes.filter((make) => make.groupId === groupId.value) ?? [])
const models = computed(() => {
  const makeIds = new Set(makes.value.map((make) => make.id))
  return data.value?.models.filter((model) => makeIds.has(model.makeId)) ?? []
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
        <Badge variant="secondary">{{ makes.length }} marcas</Badge>
        <Badge variant="outline">{{ models.length }} modelos</Badge>
      </div>
    </header>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Marcas</h2>
      <div v-if="makes.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card v-for="make in makes" :key="make.id" class="transition-shadow hover:shadow-md">
          <CardHeader>
            <CardTitle><NuxtLink :to="`/makes/${make.id}`" class="underline underline-offset-4">{{ make.name }}</NuxtLink></CardTitle>
            <CardDescription>{{ models.filter((model) => model.makeId === make.id).length }} modelos</CardDescription>
          </CardHeader>
          <CardContent>
            <NuxtLink :to="`/makes/${make.id}`" class="text-sm font-medium underline underline-offset-4">Ver marca</NuxtLink>
          </CardContent>
        </Card>
      </div>
      <Card v-else>
        <CardContent class="p-6 text-sm text-muted-foreground">Este grupo aún no tiene marcas asociadas.</CardContent>
      </Card>
    </section>

    <section v-if="models.length" class="space-y-3">
      <h2 class="text-xl font-semibold">Modelos</h2>
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <CatalogModelCard v-for="model in models" :key="model.id" :model="model" />
      </div>
    </section>
  </section>
  <section v-else class="mx-auto w-full max-w-6xl space-y-4 px-4 py-8">
    <h1>Grupo no encontrado</h1>
    <NuxtLink to="/groups" class="underline underline-offset-4">Volver a grupos</NuxtLink>
  </section>
</template>