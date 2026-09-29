<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

const comparison = useCarComparison()

const rows = computed(() => {
  const vehicles = comparison.selectedVehicles.value
  return [
    { label: 'Versión', values: vehicles.map((item) => item.variantName || 'Versión no especificada') },
    { label: 'Año modelo', values: vehicles.map((item) => String(item.vehicle.lineage.modelYear)) },
    { label: 'Precio', values: vehicles.map((item) => item.vehicle.priceAmount ? `${item.vehicle.priceAmount} ${item.vehicle.priceCurrency ?? ''}`.trim() : 'No especificado') },
    { label: 'País de armado', values: vehicles.map((item) => String(item.vehicle.assemblyCountry ?? 'No especificado')) },
    { label: 'Carrocería', values: vehicles.map((item) => String(item.vehicle.configuration.bodyStyle ?? 'No especificada')) },
    { label: 'Propulsión', values: vehicles.map((item) => String(item.vehicle.configuration.powertrain?.architecture ?? 'No especificada').replaceAll('_', ' ')) }
  ]
})
</script>

<template>
  <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-sm font-medium text-muted-foreground">Catálogo</p>
        <h1 class="text-3xl font-bold tracking-tight">Comparar autos</h1>
      </div>
      <Button as-child variant="outline">
        <NuxtLink to="/models">Añadir autos</NuxtLink>
      </Button>
    </div>

    <Card v-if="comparison.count.value < 2">
      <CardContent class="flex flex-col items-start gap-3 p-6">
        <p class="text-sm text-muted-foreground">Selecciona al menos dos autos para compararlos.</p>
        <Button as-child><NuxtLink to="/models">Explorar modelos</NuxtLink></Button>
      </CardContent>
    </Card>

    <div v-else class="overflow-x-auto rounded-md border">
      <table class="w-full min-w-[42rem] border-collapse text-left text-sm">
        <thead>
          <tr class="border-b bg-muted/40">
            <th class="w-36 p-3 font-medium text-muted-foreground">Características</th>
            <th v-for="vehicle in comparison.selectedVehicles.value" :key="vehicle.id" class="min-w-48 p-3 align-top">
              <div class="space-y-2">
                <img v-if="vehicle.image" :src="vehicle.image.url" :alt="vehicle.image.alt" class="aspect-video w-full rounded object-cover">
                <div v-else class="flex aspect-video items-center justify-center rounded bg-muted text-muted-foreground">
                  <Icon name="tabler:car" class="size-8" aria-hidden="true" />
                </div>
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <p class="font-semibold">{{ vehicle.makeName }} {{ vehicle.modelName }}</p>
                    <p class="text-xs text-muted-foreground">{{ vehicle.variantName || 'Versión no especificada' }} · {{ vehicle.year }}</p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    :aria-label="`Quitar ${vehicle.makeName} ${vehicle.modelName} ${vehicle.variantName || ''}`"
                    title="Quitar de comparación"
                    @click="comparison.remove(vehicle.id)"
                  >
                    <Icon name="tabler:x" class="size-4" aria-hidden="true" />
                  </Button>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.label" class="border-b last:border-0">
            <th scope="row" class="p-3 font-medium text-muted-foreground">{{ row.label }}</th>
            <td v-for="(value, index) in row.values" :key="index" class="p-3">{{ value }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>