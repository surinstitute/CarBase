<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { CatalogModelDetail, CatalogSafetyRating, CatalogVehicleRecord, CatalogWarrantyCoverage } from '#shared/types/catalog'

const route = useRoute()
const modelId = computed(() => String(route.params.id))
const selectedImageIndex = ref(0)
const comparison = useCarComparison()
const { data: model, status } = useQuery({
  key: () => ['model-detail', modelId.value],
  query: () => $fetch<CatalogModelDetail>(`/api/models/${encodeURIComponent(modelId.value)}`)
})
const detailImages = computed(() => {
  if (!model.value) return []
  return model.value.images.length ? model.value.images : model.value.image ? [model.value.image] : []
})
const activeImage = computed(() => detailImages.value[selectedImageIndex.value] ?? detailImages.value[0])
watch(modelId, () => {
  selectedImageIndex.value = 0
})
const modelDetailRows = computed(() => {
  if (!model.value) return []
  return [
    { field: 'id', value: model.value.id },
    { field: 'model', value: model.value.modelName },
    { field: 'generation', value: model.value.generation },
    { field: 'year', value: model.value.year },
    { field: 'created_at', value: model.value.created_at },
    { field: 'updated_at', value: model.value.updated_at },
    { field: 'make', value: model.value.makeId },
    { field: 'platform', value: model.value.platformId }
  ].map(({ field, value }) => ({ field, value: formatValue(value) }))
})

function architectureLabel(architectures: string[]) {
  return architectures.length ? architectures.map((architecture) => architecture.replaceAll('_', ' ')).join(', ') : 'No especificada'
}

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

function safetyProgramLabel(program: CatalogSafetyRating['program']) {
  const labels = {
    latin_ncap: 'Latin NCAP',
    euro_ncap: 'Euro NCAP',
    other: 'Programa de evaluación'
  }
  return labels[program]
}

function safetyMetrics(rating: CatalogSafetyRating) {
  return [
    { label: 'Ocupante adulto', value: rating.adultOccupantProtection },
    { label: 'Ocupante infantil', value: rating.childOccupantProtection },
    { label: 'Peatones y usuarios vulnerables', value: rating.vulnerableRoadUserProtection },
    { label: 'Asistencia a la seguridad', value: rating.safetyAssist }
  ]
}

function warrantyRows(warranty: CatalogModelDetail['warranty']) {
  if (!warranty) return []

  const labels = [
    { key: 'basic', label: 'Básica' },
    { key: 'drivetrain', label: 'Tren motriz' },
    { key: 'corrosion', label: 'Corrosión' }
  ] as const

  return labels.flatMap(({ key, label }) => {
    const coverage = warranty[key]
    if (!coverage) return []
    return [{ label, value: formatWarrantyCoverage(coverage) }]
  })
}

function formatWarrantyCoverage(coverage: CatalogWarrantyCoverage) {
  const terms = []
  if (coverage.years !== null) {
    terms.push(`${coverage.years} ${coverage.years === 1 ? 'año' : 'años'}`)
  }
  if (coverage.kilometersUnlimited) {
    terms.push('kilometraje ilimitado')
  } else if (coverage.kilometers !== null) {
    terms.push(`${new Intl.NumberFormat('es-MX').format(coverage.kilometers)} km`)
  }
  return terms.join(' / ')
}
</script>

<template>
  <section v-if="status === 'pending'" class="mx-auto grid w-full max-w-6xl gap-6 px-4 py-8 lg:grid-cols-2">
    <Skeleton class="aspect-4/3" />
    <Skeleton class="h-80" />
  </section>
  <section v-else-if="model" class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink :to="`/makes/${model.makeSlug}`">{{ model.makeName }}</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>{{ model.modelName }}</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
    <div class="grid items-start gap-6 lg:grid-cols-2">
      <div class="space-y-2">
        <img v-if="activeImage" :src="activeImage.url" :alt="activeImage.alt" class="aspect-4/3 w-full rounded-xl border object-cover">
        <div v-else class="flex aspect-4/3 items-center justify-center rounded-xl border bg-muted text-muted-foreground">
          <Icon name="tabler:car" class="size-12" aria-hidden="true" />
        </div>
        <div v-if="detailImages.length > 1" class="flex gap-2 overflow-x-auto">
          <button
            v-for="(image, index) in detailImages"
            :key="`${image.view}-${image.url}`"
            type="button"
            :aria-label="`Mostrar imagen ${index + 1}`"
            :aria-pressed="selectedImageIndex === index"
            class="shrink-0 overflow-hidden rounded border-2"
            :class="selectedImageIndex === index ? 'border-primary' : 'border-transparent'"
            @click="selectedImageIndex = index"
          >
            <img :src="image.url" :alt="image.alt" class="size-16 object-cover sm:size-20">
          </button>
        </div>
      </div>
      <Card>
        <CardHeader>
          <Badge variant="secondary" class="w-fit">{{ model.year }}</Badge>
          <h1 class="text-2xl font-semibold tracking-tight">{{ model.makeName }} {{ model.modelName }}</h1>
          <CardDescription>{{ model.generation || 'Modelo base' }}</CardDescription>
        </CardHeader>
        <CardContent>
          <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-3 text-sm">
            <dt class="text-muted-foreground">Año modelo</dt><dd class="font-medium">{{ model.year }}</dd>
            <dt class="text-muted-foreground">Generación</dt><dd class="font-medium">{{ model.generation || 'No especificada' }}</dd>
            <dt class="text-muted-foreground">Plataforma</dt><dd class="font-medium">{{ model.platformName || 'No especificada' }}</dd>
            <dt class="text-muted-foreground">Carrocerías</dt><dd class="font-medium">{{ model.bodyStyles.join(', ') || 'No especificadas' }}</dd>
            <dt class="text-muted-foreground">Propulsiones</dt><dd class="font-medium capitalize">{{ architectureLabel(model.architectures) }}</dd>
            <dt class="text-muted-foreground">Marca</dt><dd><NuxtLink :to="`/makes/${model.makeSlug}`" class="font-medium underline underline-offset-4">{{ model.makeName }}</NuxtLink></dd>
          </dl>
        </CardContent>
      </Card>
    </div>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Garantía</h2>
      <dl v-if="warrantyRows(model.warranty).length" class="grid gap-3 sm:grid-cols-3">
        <div v-for="row in warrantyRows(model.warranty)" :key="row.label" class="space-y-1">
          <dt class="text-sm text-muted-foreground">{{ row.label }}</dt>
          <dd class="font-medium">{{ row.value }}</dd>
        </div>
      </dl>
      <p v-else class="text-sm text-muted-foreground">No hay coberturas de garantía registradas.</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Seguridad</h2>
      <div v-if="model.safetyRatings.length" class="grid gap-4 lg:grid-cols-2">
        <Card v-for="rating in model.safetyRatings" :key="`${rating.program}-${rating.assessmentYear}`">
          <CardHeader>
            <div class="flex items-start justify-between gap-4">
              <div class="space-y-1">
                <CardTitle>{{ safetyProgramLabel(rating.program) }}</CardTitle>
                <CardDescription>Evaluación {{ rating.assessmentYear }}</CardDescription>
              </div>
              <a v-if="rating.sourceUrl" :href="rating.sourceUrl" target="_blank" rel="noreferrer" class="text-sm font-medium underline underline-offset-4">Fuente</a>
            </div>
          </CardHeader>
          <CardContent class="space-y-5">
            <div class="flex items-center gap-1" :aria-label="`${rating.overallStars} de 5 estrellas`">
              <Icon v-for="star in 5" :key="star" name="tabler:star-filled" :class="star <= rating.overallStars ? 'size-6 text-amber-400' : 'size-6 text-muted'" aria-hidden="true" />
              <span class="ml-2 text-sm font-medium">{{ rating.overallStars }}/5</span>
            </div>
            <dl class="grid gap-x-6 gap-y-4 sm:grid-cols-2">
              <div v-for="metric in safetyMetrics(rating)" :key="metric.label" class="space-y-1">
                <dt class="text-sm text-muted-foreground">{{ metric.label }}</dt>
                <dd class="text-lg font-semibold tabular-nums">{{ metric.value }}%</dd>
              </div>
            </dl>
          </CardContent>
        </Card>
      </div>
      <p v-else class="text-sm text-muted-foreground">No hay evaluaciones de seguridad registradas para este modelo.</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Variantes <span class="text-muted-foreground">({{ model.vehicles.length }})</span></h2>
      <div v-if="model.vehicles.length" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <CatalogVehicleCard v-for="(vehicle, index) in model.vehicles" :key="vehicle.id" :model="model" :vehicle="vehicle" :index="index" />
      </div>
      <p v-else class="text-sm text-muted-foreground">No hay variantes registradas para este modelo.</p>
    </section>

    <Collapsible class="space-y-3">
      <CollapsibleTrigger as-child>
        <Button variant="outline" class="w-full justify-between">
          <span>Atributos originales del modelo</span>
          <Icon name="tabler:chevron-down" class="size-4" aria-hidden="true" />
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <Table>
          <TableCaption>Atributos del recurso de modelo.</TableCaption>
          <TableHeader>
            <TableRow>
              <TableHead>Campo</TableHead>
              <TableHead>Valor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="row in modelDetailRows" :key="row.field">
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
    <h1>Modelo no encontrado</h1>
    <NuxtLink to="/models">Volver a modelos</NuxtLink>
  </section>
</template>