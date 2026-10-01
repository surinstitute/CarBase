<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatNumber } from '@/lib/utils'
import type { CatalogModel, CatalogVehicleRecord } from '#shared/types/catalog'

type VehicleCardModel = Pick<CatalogModel, 'id' | 'makeId' | 'makeName' | 'modelName' | 'image'>

const props = defineProps<{
  model: VehicleCardModel
  vehicle: CatalogVehicleRecord
  index?: number
}>()

const comparison = useCarComparison()
const image = computed(() => props.vehicle.images?.leftSide ?? props.vehicle.images?.silhouette ?? props.vehicle.images?.front)
const isSelected = computed(() => comparison.selectedVehicles.value.some((selected) => selected.id === String(props.vehicle.id)))

function variantLabel() {
  return props.vehicle.variantName || `Variante ${(props.index ?? 0) + 1}`
}

function configurationRows() {
  const powertrain = props.vehicle.configuration.powertrain
  if (!powertrain) return []

  const rows: Array<{ field: string; value: string }> = []
  if (powertrain.architecture) {
    rows.push({ field: 'Arquitectura', value: powertrain.architecture.replaceAll('_', ' ') })
  }
  const energyStorage = formatEnergyStorage(powertrain.energyStorage)
  if (energyStorage) {
    rows.push({ field: 'Almacenamiento de energía', value: energyStorage })
  }
  return rows
}

function formatEnergyStorage(value: unknown) {
  if (!Array.isArray(value)) return ''

  return value.map((item: unknown) => {
    if (!item || typeof item !== 'object') return ''
    const storage = item as Record<string, unknown>
    const type = typeof storage.type === 'string' ? storage.type.replaceAll('_', ' ') : ''
    const capacity = typeof storage.capacityKwh === 'number'
      ? `${formatNumber(storage.capacityKwh)} kWh`
      : typeof storage.fuelCapacity === 'number'
        ? `${formatNumber(storage.fuelCapacity)} L`
        : ''
    return [type, capacity].filter(Boolean).join(' · ')
  }).filter(Boolean).join(', ')
}
</script>

<template>
  <Card class="h-full gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
    <NuxtLink :to="`/models/variants/${model.id}/${vehicle.id}`" class="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
      <img v-if="image" :src="image.url" :alt="image.alt" class="aspect-2/1 w-full object-cover">
      <div v-else class="flex aspect-2/1 w-full items-center justify-center bg-muted text-muted-foreground">
        <Icon name="tabler:car" class="size-10" aria-hidden="true" />
      </div>
    </NuxtLink>
    <CardHeader class="pt-6 pb-2">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0 space-y-1">
          <CardDescription>{{ model.makeName }} {{ model.modelName }}</CardDescription>
          <CardTitle>
            <NuxtLink :to="`/models/variants/${model.id}/${vehicle.id}`" class="underline underline-offset-4">
              {{ variantLabel() }}
            </NuxtLink>
          </CardTitle>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <Badge variant="secondary">{{ vehicle.lineage.modelYear }}</Badge>
          <Button
            type="button"
            variant="outline"
            size="icon"
            class="size-9 rounded-full"
            :aria-label="isSelected ? `Quitar ${variantLabel()} de comparación` : `Añadir ${variantLabel()} a comparación`"
            :title="isSelected ? 'Quitar de comparación' : comparison.isAtLimit.value ? 'Máximo de 4 autos seleccionados' : 'Añadir a comparación'"
            :aria-pressed="isSelected"
            :disabled="!isSelected && comparison.isAtLimit.value"
            @click="comparison.toggle(model, vehicle)"
          >
            <Icon :name="isSelected ? 'tabler:minus' : 'tabler:plus'" class="size-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </CardHeader>
    <CardContent class="space-y-3 pb-6">
      <dl class="grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-x-4 gap-y-3 text-sm">
        <dt class="text-muted-foreground">Generación</dt>
        <dd class="font-medium">{{ vehicle.lineage.generationId ?? 'No especificada' }}</dd>
        <template v-if="vehicle.priceAmount">
          <dt class="text-muted-foreground">Precio</dt>
          <dd class="font-medium">{{ vehicle.priceCurrency }} {{ formatNumber(vehicle.priceAmount) }}</dd>
        </template>
        <template v-for="row in configurationRows()" :key="row.field">
          <dt class="text-muted-foreground">{{ row.field }}</dt>
          <dd class="wrap-break-word font-medium">{{ row.value }}</dd>
        </template>
      </dl>
      <p v-if="!configurationRows().length" class="text-sm text-muted-foreground">
        Configuración aún no especificada.
      </p>
    </CardContent>
  </Card>
</template>