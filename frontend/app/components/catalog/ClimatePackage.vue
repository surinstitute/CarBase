<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { CatalogVehicleRecord } from '#shared/types/catalog'

const props = defineProps<{
  climate: CatalogVehicleRecord['climate']
}>()

const climateFeatures = [
  { key: 'automaticClimateControl', label: 'Climatización automática' },
  { key: 'rearClimateControl', label: 'Climatización trasera' },
  { key: 'cabinAirFilter', label: 'Filtro de aire de cabina' },
  { key: 'airPurificationSystem', label: 'Sistema de purificación de aire' },
  { key: 'remotePreconditioning', label: 'Preacondicionamiento remoto' },
  { key: 'heatPump', label: 'Bomba de calor' },
  { key: 'heatedFrontSeats', label: 'Asientos delanteros calefactables' },
  { key: 'heatedRearSeats', label: 'Asientos traseros calefactables' },
  { key: 'heatedSteeringWheel', label: 'Volante calefactable' }
] as const

const climateMeasurements = [
  { key: 'refrigerantType', label: 'Refrigerante' },
  { key: 'refrigerantGwp', label: 'GWP del refrigerante' },
  { key: 'compressorType', label: 'Tipo de compresor' },
  { key: 'coolingCapacity', label: 'Capacidad de enfriamiento' },
  { key: 'coolingPowerDraw', label: 'Potencia en enfriamiento' },
  { key: 'coolingCop', label: 'COP de enfriamiento' },
  { key: 'refrigerantCharge', label: 'Carga de refrigerante' }
] as const

function valueOf(value: unknown) {
  if (value && typeof value === 'object' && 'value' in value && 'unit' in value) {
    const measurement = value as { value: number, unit: string }
    return `${measurement.value} ${measurement.unit}`
  }
  return String(value)
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Climatización</CardTitle>
      <CardDescription>{{ climate?.name ?? 'Paquete de climatización' }}</CardDescription>
    </CardHeader>
    <CardContent>
      <dl v-if="climate" class="grid gap-x-8 gap-y-3 text-sm md:grid-cols-2">
        <div v-if="climate.zoneCount !== undefined" class="flex items-baseline justify-between gap-4">
          <dt class="text-muted-foreground">Zonas</dt>
          <dd class="font-medium">{{ climate.zoneCount }}</dd>
        </div>
        <div v-for="feature in climateFeatures" :key="feature.key" class="flex items-baseline justify-between gap-4">
          <dt class="text-muted-foreground">{{ feature.label }}</dt>
          <dd class="font-medium">{{ climate[feature.key] ? 'Disponible' : 'No disponible' }}</dd>
        </div>
        <div v-for="measurement in climateMeasurements.filter((item) => climate[item.key] !== undefined)" :key="measurement.key" class="flex items-baseline justify-between gap-4">
          <dt class="text-muted-foreground">{{ measurement.label }}</dt>
          <dd class="font-medium">{{ valueOf(climate[measurement.key]) }}</dd>
        </div>
      </dl>
      <p v-else class="text-sm text-muted-foreground">No hay paquete de climatización registrado para esta variante.</p>
    </CardContent>
  </Card>
</template>
