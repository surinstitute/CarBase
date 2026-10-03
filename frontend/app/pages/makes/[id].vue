<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { countryFlag } from '@/lib/utils'
import type { CatalogResponse } from '#shared/types/catalog'

interface ModelCard {
  id: string
  model: CatalogResponse['models'][number]
  years: number[]
  bodyStyles: string[]
  generations: string[]
}

const route = useRoute()
const makeSlug = computed(() => String(route.params.id))
const { data, status } = useQuery({
  key: ['catalog'],
  query: () => $fetch<CatalogResponse>('/api/catalog')
})
const make = computed(() => data.value?.makes.find((item) => item.slug === makeSlug.value))
const models = computed(() => data.value?.models.filter((model) => model.makeId === make.value?.id) ?? [])
const modelCards = computed<ModelCard[]>(() => {
  const cards = new Map<string, ModelCard>()

  for (const model of models.value) {
    const card = cards.get(model.modelName)
    if (card) {
      card.years.push(model.year)
      card.bodyStyles = [...new Set([...card.bodyStyles, ...model.bodyStyles])]
      if (model.generation && !card.generations.includes(model.generation)) {
        card.generations.push(model.generation)
      }
      continue
    }
    cards.set(model.modelName, {
      id: model.modelName,
      model,
      years: [model.year],
      bodyStyles: model.bodyStyles,
      generations: model.generation ? [model.generation] : []
    })
  }

  return [...cards.values()]
})
</script>

<template>
  <section v-if="status === 'pending'" class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Skeleton class="h-8 w-48" />
    <Skeleton class="h-16 w-full" />
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><Skeleton v-for="item in 3" :key="item" class="h-80" /></div>
  </section>
  <section v-else-if="status === 'error'" class="mx-auto w-full max-w-6xl px-4 py-8">
    <p role="alert" class="text-sm text-destructive">No se pudo cargar la información de marcas.</p>
  </section>
  <section v-else-if="make" class="mx-auto w-full max-w-6xl space-y-8 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>{{ make.name }}</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <header class="flex flex-wrap items-end justify-between gap-4 border-b pb-6">
      <div class="space-y-2">
        <p class="text-sm text-muted-foreground">Marca</p>
        <h1 class="text-3xl font-bold tracking-tight">{{ make.name }}</h1>
        <p v-if="make.country" class="text-sm text-muted-foreground">{{ countryFlag(make.country) }} Origen: {{ make.country }}</p>
      </div>
      <Badge variant="secondary">{{ modelCards.length }} modelos</Badge>
    </header>

    <div v-if="modelCards.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <CatalogModelCard v-for="card in modelCards" :key="card.id" :model="card.model" :years="card.years" :body-styles="card.bodyStyles" :generations="card.generations" :show-body-styles="false" />
    </div>
    <Card v-else>
      <CardContent class="p-6 text-sm text-muted-foreground">Esta marca aún no tiene modelos base en el catálogo.</CardContent>
    </Card>
  </section>
  <section v-else class="mx-auto w-full max-w-6xl space-y-4 px-4 py-8">
    <h1>Marca no encontrada</h1>
    <NuxtLink to="/models" class="underline underline-offset-4">Volver a modelos</NuxtLink>
  </section>
</template>