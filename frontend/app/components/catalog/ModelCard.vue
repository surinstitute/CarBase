<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { CatalogModel } from '#shared/types/catalog'

type ModelCardModel = Pick<
  CatalogModel,
  | 'id'
  | 'makeSlug'
  | 'makeName'
  | 'modelName'
  | 'year'
  | 'generation'
  | 'platformName'
  | 'bodyStyles'
  | 'architectures'
  | 'image'
>

const props = defineProps<{
  model: ModelCardModel
  years?: number[]
  bodyStyles?: string[]
  generations?: string[]
  generationLinks?: Array<{ label: string, route: string }>
  showBodyStyles?: boolean
}>()

const modelOverviewRoute = computed(() => (
  `/makes/${encodeURIComponent(props.model.makeSlug)}/models/${encodeURIComponent(props.model.modelName)}`
))
const yearLabel = computed(() => {
  const years = props.years?.length ? props.years : [props.model.year]
  const startYear = Math.min(...years)
  const endYear = Math.max(...years)
  return startYear === endYear ? String(startYear) : `${startYear} - ${endYear}`
})
const visibleBodyStyles = computed(() => props.bodyStyles?.length ? props.bodyStyles : props.model.bodyStyles)
const visibleGenerations = computed(() => props.generations?.length
  ? props.generations
  : props.model.generation ? [props.model.generation] : [])
const generationLabel = computed(() => {
  const parsed = visibleGenerations.value.map((generation) => {
    const match = generation.match(/^(.*?)(\d+)$/)
    return match ? { prefix: match[1], number: Number(match[2]) } : null
  })

  if (!parsed.length || parsed.some((generation) => !generation) || new Set(parsed.map((generation) => generation!.prefix)).size !== 1) {
    return visibleGenerations.value.join(', ')
  }

  const prefix = parsed[0]!.prefix
  const numbers = [...new Set(parsed.map((generation) => generation!.number))].sort((left, right) => left - right)
  const ranges: string[] = []
  let start = numbers[0]
  let end = numbers[0]

  for (const number of numbers.slice(1)) {
    if (number === end + 1) {
      end = number
      continue
    }
    ranges.push(start === end ? `${prefix}${start}` : `${prefix}${start}-${end}`)
    start = number
    end = number
  }
  ranges.push(start === end ? `${prefix}${start}` : `${prefix}${start}-${end}`)

  return ranges.join(', ')
})

function architectureLabel(architecture: string) {
  const labels: Record<string, string> = {
    ice: 'Combustión',
    mild_hybrid: 'Mild hybrid',
    series_hybrid: 'Híbrido serie',
    parallel_hybrid: 'Híbrido paralelo',
    power_split_hybrid: 'Híbrido',
    plug_in_hybrid: 'Híbrido enchufable',
    battery_electric: 'Eléctrico',
    fuel_cell_electric: 'Pila de combustible'
  }

  return labels[architecture] ?? architecture.replaceAll('_', ' ')
}
</script>

<template>
  <Card class="h-full gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
    <NuxtLink :to="modelOverviewRoute" class="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
      <img v-if="model.image" :src="model.image.url" :alt="model.image.alt" class="aspect-2/1 w-full object-cover">
      <div v-else class="flex aspect-2/1 w-full items-center justify-center bg-muted text-muted-foreground">
        <Icon name="tabler:car" class="size-10" aria-hidden="true" />
      </div>
    </NuxtLink>
    <CardHeader class="pt-6 pb-2">
      <Badge v-if="!visibleGenerations.length" variant="secondary" class="w-fit">{{ yearLabel }}</Badge>
      <CardTitle>
        <NuxtLink :to="modelOverviewRoute" class="transition-colors hover:text-muted-foreground">{{ model.modelName }}</NuxtLink>
      </CardTitle>
      <CardDescription>
        <NuxtLink :to="`/makes/${model.makeSlug}`" class="hover:text-foreground">{{ model.makeName }}</NuxtLink>
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-3 pb-6">
      <p v-if="model.platformName" class="text-sm text-muted-foreground">{{ model.platformName }}</p>
      <div class="flex flex-wrap gap-2">
        <template v-if="generationLinks?.length">
          <NuxtLink
            v-for="generation in generationLinks"
            :key="generation.route"
            :to="generation.route"
            class="rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <Badge variant="secondary">{{ generation.label }}</Badge>
          </NuxtLink>
        </template>
        <Badge v-else-if="generationLabel" variant="secondary">{{ generationLabel }}</Badge>
        <Badge v-if="visibleGenerations.length" variant="outline">{{ yearLabel }}</Badge>
        <Badge v-if="showBodyStyles !== false" v-for="bodyStyle in visibleBodyStyles" :key="bodyStyle" variant="outline">{{ bodyStyle }}</Badge>
        <Badge v-for="architecture in model.architectures" :key="architecture" variant="outline">{{ architectureLabel(architecture) }}</Badge>
      </div>
    </CardContent>
  </Card>
</template>