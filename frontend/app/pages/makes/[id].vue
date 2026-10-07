<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { countryFlag, countryName } from '@/lib/utils'
import type { ApiPage, CatalogMake, CatalogModel } from '#shared/types/catalog'

interface ModelCard {
  id: string
  model: CatalogModel
  years: number[]
  bodyStyles: string[]
  generations: string[]
}

const route = useRoute()
const makeSlug = computed(() => String(route.params.id))
const { data: makes, status: makesStatus } = useQuery({
  key: ['makes'],
  query: () => $fetch<ApiPage<CatalogMake>>('/api/makes')
})
const { data: models, status: modelsStatus } = useQuery({
  key: ['models'],
  query: () => $fetch<ApiPage<CatalogModel>>('/api/models')
})
const status = computed(() => (
  makesStatus.value === 'error' || modelsStatus.value === 'error'
    ? 'error'
    : makesStatus.value === 'pending' || modelsStatus.value === 'pending'
      ? 'pending'
      : 'success'
))
const make = computed(() => makes.value?.results.find((item) => item.slug === makeSlug.value || item.id === makeSlug.value))
const makeModels = computed(() => models.value?.results.filter((model) => model.makeId === make.value?.id) ?? [])
const modelCards = computed<ModelCard[]>(() => {
  const cards = new Map<string, ModelCard>()

  for (const model of makeModels.value) {
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

    <header class="space-y-5 border-b pb-6">
      <div>
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <img v-if="make.iconSvg" :src="make.iconSvg" alt="" class="size-16 object-contain">
            <h1 class="text-3xl font-bold tracking-tight">{{ make.name }}</h1>
          </div>
          <Badge variant="secondary">{{ modelCards.length }} modelos</Badge>
        </div>

        <div v-if="make.country || make.legalRepresentative" class="border-b pb-4 text-sm text-muted-foreground">
          <p v-if="make.legalRepresentative">{{ make.legalRepresentative }}</p>
          <p v-if="make.country" class="flex items-center gap-2">Origen: {{ countryName(make.country) }} ({{ make.country }}) <span class="text-2xl leading-none" aria-hidden="true">{{ countryFlag(make.country) }}</span></p>
        </div>
      </div>

      <section v-if="make.description" class="space-y-2" aria-labelledby="make-description-heading">
        <h2 id="make-description-heading" class="text-sm font-semibold">Descripción</h2>
        <p class="max-w-3xl text-sm leading-relaxed text-muted-foreground">{{ make.description }}</p>
      </section>

      <section v-if="make.phone || make.website" class="space-y-2 border-t pt-4" aria-labelledby="make-contact-heading">
        <h2 id="make-contact-heading" class="text-sm font-semibold">Contacto</h2>
        <div class="flex flex-wrap gap-x-5 gap-y-2 text-sm">
          <a v-if="make.phone" :href="`tel:${make.phone}`" class="inline-flex items-center gap-2 underline underline-offset-4"><Icon name="tabler:phone" class="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />{{ make.phone }}</a>
          <a v-if="make.website" :href="make.website" target="_blank" rel="noreferrer" class="inline-flex items-center gap-2 underline underline-offset-4"><Icon name="tabler:world" class="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />Visitar sitio<Icon name="tabler:external-link" class="size-4 shrink-0" aria-hidden="true" /></a>
        </div>
      </section>
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