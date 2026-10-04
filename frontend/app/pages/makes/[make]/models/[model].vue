<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { ApiPage, CatalogMake, CatalogModel } from '#shared/types/catalog'

interface GenerationGroup {
  id: string
  label: string
  years: number[]
  bodyStyles: Array<{
    name: string
    model: CatalogModel
  }>
}

const route = useRoute()
const makeSlug = computed(() => String(route.params.make))
const modelName = computed(() => String(route.params.model))

const { data: makes, status: makesStatus } = useQuery({
  key: ['makes'],
  query: () => $fetch<ApiPage<CatalogMake>>('/api/makes')
})
const make = computed(() => makes.value?.results.find((item) => item.slug === makeSlug.value))
const { data: modelPage, status: modelsStatus } = useQuery({
  key: () => ['model-overview', make.value?.id, modelName.value],
  query: () => $fetch<ApiPage<CatalogModel>>('/api/models', {
    query: {
      model: modelName.value,
      ...(make.value ? { make: make.value.id } : {})
    }
  })
})
const status = computed(() => (
  makesStatus.value === 'error' || modelsStatus.value === 'error'
    ? 'error'
    : makesStatus.value === 'pending' || modelsStatus.value === 'pending'
      ? 'pending'
      : 'success'
))
const models = computed(() => modelPage.value?.results ?? [])
const generations = computed<GenerationGroup[]>(() => {
  const groups = new Map<string, GenerationGroup>()

  for (const model of models.value) {
    const group = groups.get(model.modelGenerationId)
    if (group) {
      group.years.push(model.year)
      for (const name of model.bodyStyles.length ? model.bodyStyles : ['Carrocería no especificada']) {
        if (!group.bodyStyles.some((bodyStyle) => bodyStyle.name === name)) {
          group.bodyStyles.push({ name, model })
        }
      }
      continue
    }
    groups.set(model.modelGenerationId, {
      id: model.modelGenerationId,
      label: model.generation || 'Generación no especificada',
      years: [model.year],
      bodyStyles: (model.bodyStyles.length ? model.bodyStyles : ['Carrocería no especificada']).map((name) => ({ name, model }))
    })
  }

  return [...groups.values()].sort((left, right) => Math.min(...left.years) - Math.min(...right.years))
})

function yearLabel(years: number[]) {
  const startYear = Math.min(...years)
  const endYear = Math.max(...years)
  return startYear === endYear ? String(startYear) : `${startYear} - ${endYear}`
}
</script>

<template>
  <section v-if="status === 'pending'" class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Skeleton class="h-8 w-48" />
    <Skeleton class="h-24 w-full" />
    <Skeleton v-for="item in 3" :key="item" class="h-64" />
  </section>
  <section v-else-if="status === 'error'" class="mx-auto w-full max-w-6xl px-4 py-8">
    <p role="alert" class="text-sm text-destructive">No se pudo cargar el modelo.</p>
  </section>
  <section v-else-if="make && models.length" class="mx-auto w-full max-w-6xl space-y-8 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink :to="`/makes/${make.slug}`">{{ make.name }}</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>{{ modelName }}</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <header class="flex flex-wrap items-end justify-between gap-4 border-b pb-6">
      <div class="space-y-2">
        <p class="text-sm text-muted-foreground">{{ make.name }}</p>
        <h1 class="text-3xl font-bold tracking-tight">{{ modelName }}</h1>
      </div>
      <Badge variant="secondary">{{ generations.length }} generaciones</Badge>
    </header>

    <div class="space-y-8">
      <section
        v-for="generation in generations"
        :key="generation.id"
        class="space-y-3"
      >
        <div>
          <h2 class="text-xl font-semibold">{{ generation.label }}</h2>
          <p class="text-sm text-muted-foreground">{{ yearLabel(generation.years) }}</p>
        </div>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
            v-for="bodyStyle in generation.bodyStyles"
            :key="bodyStyle.name"
            :to="`/models/${bodyStyle.model.id}`"
            class="block rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <Card class="h-full transition-colors hover:bg-muted/50">
              <CardHeader>
                <CardTitle>{{ bodyStyle.name }}</CardTitle>
                <CardDescription>Ver años y versiones</CardDescription>
              </CardHeader>
            </Card>
          </NuxtLink>
        </div>
      </section>
    </div>
  </section>
  <section v-else class="mx-auto w-full max-w-6xl space-y-4 px-4 py-8">
    <h1 class="text-2xl font-semibold">Modelo no encontrado</h1>
    <NuxtLink to="/models" class="underline underline-offset-4">Volver a modelos</NuxtLink>
  </section>
</template>