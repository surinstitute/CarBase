<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import type { CatalogResponse, CatalogVehicleRecord } from '#shared/types/catalog'

const route = useRoute()
const modelId = computed(() => String(route.params.modelId))
const variantId = computed(() => String(route.params.variantId))
const { data, status } = useQuery({
  key: ['catalog'],
  query: () => $fetch<CatalogResponse>('/api/catalog')
})
const model = computed(() => data.value?.models.find((item) => item.id === modelId.value))
const variantIndex = computed(() => model.value?.vehicles.findIndex((item) => String(item.id) === variantId.value) ?? -1)
const variant = computed(() => variantIndex.value >= 0 ? model.value?.vehicles[variantIndex.value] : undefined)
const variantNumber = computed(() => variantIndex.value + 1)
const variantLabel = computed(() => variant.value?.variantName || `Variante ${variantNumber.value}`)
const image = computed(() => variant.value?.images?.leftSide
  ?? variant.value?.images?.silhouette
  ?? variant.value?.images?.front
  ?? variant.value?.images?.rightSide
  ?? variant.value?.images?.rear)
const detailRows = computed(() => variant.value
  ? Object.entries(variant.value).map(([field, value]) => ({ field, value: formatValue(value) }))
  : [])

function formatValue(value: unknown) {
  if (value === null) return 'null'
  if (typeof value === 'object') return JSON.stringify(value, null, 2) ?? ''
  return String(value)
}

function configurationRows(vehicle: CatalogVehicleRecord) {
  return Object.entries(vehicle.configuration)
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .map(([field, value]) => ({ field, value: formatValue(value) }))
}
</script>

<template>
  <section v-if="status === 'pending'" class="mx-auto grid w-full max-w-6xl gap-6 px-4 py-8 lg:grid-cols-2">
    <Skeleton class="aspect-4/3" />
    <Skeleton class="h-80" />
  </section>
  <section v-else-if="model && variant" class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink :to="`/makes/${model.makeId}`">{{ model.makeName }}</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink :to="`/models/${model.id}`">{{ model.modelName }}</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>{{ variantLabel }}</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <div class="grid items-start gap-6 lg:grid-cols-2">
      <img v-if="image" :src="image.url" :alt="image.alt" class="aspect-4/3 w-full rounded-xl border object-cover">
      <div v-else class="flex aspect-4/3 items-center justify-center rounded-xl border bg-muted text-muted-foreground">
        <Icon name="tabler:car" class="size-12" aria-hidden="true" />
      </div>
      <Card>
        <CardHeader>
          <Badge variant="secondary" class="w-fit">{{ variant.lineage.modelYear }}</Badge>
          <h1 class="text-2xl font-semibold tracking-tight">{{ model.makeName }} {{ model.modelName }} · {{ variantLabel }}</h1>
          <CardDescription>Registro de vehículo #{{ variant.id }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-sm">
            <dt class="text-muted-foreground">Año modelo</dt><dd class="font-medium">{{ variant.lineage.modelYear }}</dd>
            <dt class="text-muted-foreground">Generación</dt><dd class="font-medium">{{ variant.lineage.generationId ?? 'No especificada' }}</dd>
            <template v-for="row in configurationRows(variant)" :key="row.field">
              <dt class="text-muted-foreground">{{ row.field }}</dt>
              <dd class="wrap-break-word font-medium">{{ row.value }}</dd>
            </template>
          </dl>
          <p v-if="!configurationRows(variant).length" class="text-sm text-muted-foreground">
            No hay datos de configuración disponibles para esta variante.
          </p>
        </CardContent>
      </Card>
    </div>

    <Collapsible class="space-y-3">
      <CollapsibleTrigger as-child>
        <Button variant="outline" class="w-full justify-between">
          <span>Datos completos de la variante</span>
          <Icon name="tabler:chevron-down" class="size-4" aria-hidden="true" />
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <Table>
          <TableCaption>Campos del registro original de esta variante.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Campo</TableHead>
              <TableHead>Valor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="row in detailRows" :key="row.field">
              <TableCell class="whitespace-nowrap font-mono text-xs">{{ row.field }}</TableCell>
              <TableCell class="max-w-2xl whitespace-normal">
                <pre class="whitespace-pre-wrap break-all font-mono text-xs">{{ row.value }}</pre>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CollapsibleContent>
    </Collapsible>
  </section>
  <section v-else class="mx-auto w-full max-w-6xl space-y-4 px-4 py-8">
    <h1>{{ model ? 'Variante no encontrada' : 'Modelo no encontrado' }}</h1>
    <NuxtLink :to="model ? `/models/${model.id}` : '/models'" class="underline underline-offset-4">
      {{ model ? 'Volver al modelo' : 'Volver a modelos' }}
    </NuxtLink>
  </section>
</template>