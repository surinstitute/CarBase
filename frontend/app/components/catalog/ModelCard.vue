<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { CatalogModel } from '#shared/types/catalog'

const props = defineProps<{
  model: CatalogModel
}>()

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
    <NuxtLink :to="`/models/${model.id}`" class="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
      <img v-if="model.image" :src="model.image.url" :alt="model.image.alt" class="aspect-2/1 w-full object-cover">
      <div v-else class="flex aspect-2/1 w-full items-center justify-center bg-muted text-muted-foreground">
        <Icon name="tabler:car" class="size-10" aria-hidden="true" />
      </div>
    </NuxtLink>
    <CardHeader class="pt-6 pb-2">
      <Badge variant="secondary" class="w-fit">{{ model.year }}</Badge>
      <CardTitle>
        <NuxtLink :to="`/models/${model.id}`" class="transition-colors hover:text-muted-foreground">{{ model.modelName }}</NuxtLink>
      </CardTitle>
      <CardDescription>
        <NuxtLink :to="`/makes/${model.makeSlug}`" class="hover:text-foreground">{{ model.makeName }}</NuxtLink>
        <span v-if="model.generation"> · {{ model.generation }}</span>
      </CardDescription>
    </CardHeader>
    <CardContent class="space-y-3 pb-6">
      <p v-if="model.platformName" class="text-sm text-muted-foreground">{{ model.platformName }}</p>
      <div class="flex flex-wrap gap-2">
        <Badge v-for="bodyStyle in model.bodyStyles" :key="bodyStyle" variant="outline">{{ bodyStyle }}</Badge>
        <Badge v-for="architecture in model.architectures" :key="architecture" variant="outline">{{ architectureLabel(architecture) }}</Badge>
      </div>
    </CardContent>
  </Card>
</template>