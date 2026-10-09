<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import type { ComparisonVehicle } from '@/composables/useCarComparison'
import { powertrainArchitectureLabel } from '@/lib/powertrain'
import { countryName, formatNumber } from '@/lib/utils'
import type { CatalogSafetyRating } from '#shared/types/catalog'

const comparison = useCarComparison()
const selectedVehicles = computed<ComparisonVehicle[]>(() => comparison.selectedVehicles.value)
const safetyRatings = ref<Record<string, CatalogSafetyRating[]>>({})
const missingValue = 'No especificado'

function latestSafetyRating(modelId: string) {
  return safetyRatings.value[modelId]?.[0]
}

function safetyProgramLabel(program: CatalogSafetyRating['program']) {
  const labels = {
    latin_ncap: 'Latin NCAP',
    euro_ncap: 'Euro NCAP',
    other: 'Programa de evaluación'
  }
  return labels[program]
}

watch(
  () => [...new Set(selectedVehicles.value.map((vehicle: ComparisonVehicle) => vehicle.modelId))],
  async (modelIds: string[]) => {
    const ratings = await Promise.all(modelIds.map(async (modelId: string) => [
      modelId,
      await $fetch<CatalogSafetyRating[]>(`/api/models/${encodeURIComponent(modelId)}/safety-ratings`)
    ] as const))
    safetyRatings.value = Object.fromEntries(ratings)
  },
  { immediate: true }
)

const comparisonSections = computed(() => {
  const vehicles: ComparisonVehicle[] = selectedVehicles.value
  const sections = [
    {
      title: 'Información general',
      rows: [
        { label: 'Versión', values: vehicles.map((item: ComparisonVehicle) => item.variantName || 'Versión no especificada') },
        { label: 'Año modelo', values: vehicles.map((item: ComparisonVehicle) => String(item.vehicle.lineage.modelYear)) },
        { label: 'Precio', values: vehicles.map((item: ComparisonVehicle) => item.vehicle.priceAmount ? `${formatNumber(item.vehicle.priceAmount)} ${item.vehicle.priceCurrency ?? ''}`.trim() : missingValue) },
        { label: 'País de armado', values: vehicles.map((item: ComparisonVehicle) => countryName(item.vehicle.assemblyCountry) || missingValue) },
        { label: 'Carrocería', values: vehicles.map((item: ComparisonVehicle) => String(item.vehicle.configuration.bodyStyle ?? missingValue)) }
      ]
    },
    {
      title: 'Evaluación NCAP',
      rows: [{
        label: 'Resultado',
        values: vehicles.map((vehicle: ComparisonVehicle) => latestSafetyRating(vehicle.modelId))
      }]
    },
    { title: 'Especificaciones', rows: groupedRows(vehicles, generalSpecificationRows) },
    { title: 'Almacenamiento', rows: groupedRows(vehicles, storageSpecificationRows) },
    { title: 'Rendimiento', rows: groupedRows(vehicles, vehiclePerformanceRows) },
    { title: 'Configuración', rows: groupedRows(vehicles, configurationRows) },
    { title: 'Climatización', rows: groupedRows(vehicles, climateRows) },
    { title: 'Seguridad', rows: groupedRows(vehicles, vehicleSafetyRows) }
  ].filter((section) => section.rows.length)

  return sections
})

function groupedRows(vehicles: ComparisonVehicle[], rowsForVehicle: (vehicle: ComparisonVehicle) => Array<{ label: string, value: string }>) {
  const rowsByVehicle = vehicles.map(rowsForVehicle)
  const labels = [...new Set(rowsByVehicle.flatMap((rows) => rows.map((row) => row.label)))]
  return labels.map((label) => ({
    label,
    values: rowsByVehicle.map((rows) => rows.find((row) => row.label === label)?.value ?? missingValue)
  }))
}

function specificationRows(item: ComparisonVehicle) {
  return Object.entries(recordOf(item.vehicle.specs)).map(([field, value]) => ({
    key: field,
    label: specificationLabel(field),
    value: measurement(value)
  }))
}

const storageSpecificationKeys = new Set([
  'trunkCapacity',
  'cargoFloorWidthBetweenWheelHouses',
  'frontCargoCapacity',
  'maxCargoCapacitySeatsFolded'
])

function generalSpecificationRows(item: ComparisonVehicle) {
  return specificationRows(item).filter((row) => !storageSpecificationKeys.has(row.key))
}

function storageSpecificationRows(item: ComparisonVehicle) {
  return specificationRows(item).filter((row) => storageSpecificationKeys.has(row.key))
}

function vehiclePerformanceRows(item: ComparisonVehicle) {
  return Object.entries(recordOf(item.vehicle.performance)).flatMap(([category, values]) =>
    itemsOf(values).map((value) => {
      const detail = [label(value.cycle), label(value.scope)].filter(Boolean).join(' · ')
      return {
        label: [specificationLabel(category), label(value.metric) || 'Resultado', detail].filter(Boolean).join(' · '),
        value: `${formatNumber(String(value.value)) || '—'} ${label(value.unit) || value.unit || ''}`.trim()
      }
    })
  )
}

function configurationRows(item: ComparisonVehicle) {
  const configuration = recordOf(item.vehicle.configuration)
  const powertrain = recordOf(configuration.powertrain)
  const charging = recordOf(configuration.charging)
  const rows: Array<{ label: string, value: string }> = []
  const energySources = itemsOf(powertrain.energySources).map((source) => label(source.source)).filter(Boolean)
  const energyStorage = itemsOf(powertrain.energyStorage).map((storage) => [label(storage.type), storage.capacityKwh !== undefined ? `${formatNumber(String(storage.capacityKwh))} kWh` : ''].filter(Boolean).join(' · ')).filter(Boolean)
  const energyConverters = itemsOf(powertrain.energyConverters).map((converter) => label(converter.type)).filter(Boolean)
  const tractionMotors = itemsOf(powertrain.tractionMotors).map((motor) => [label(motor.role), label(motor.position), motor.quantity ? `x${formatNumber(String(motor.quantity))}` : ''].filter(Boolean).join(' · ')).filter(Boolean)
  const ports = itemsOf(charging.ports).map((port) => [label(port.currentType), label(port.connector), label(port.location)].filter(Boolean).join(' · ')).filter(Boolean)

  if (powertrain.architecture) rows.push({ label: 'Propulsión', value: label(powertrain.architecture) })
  if (energySources.length) rows.push({ label: 'Fuente de energía', value: energySources.join(', ') })
  if (energyStorage.length) rows.push({ label: 'Almacenamiento', value: energyStorage.join(', ') })
  if (energyConverters.length) rows.push({ label: 'Convertidores', value: energyConverters.join(', ') })
  if (tractionMotors.length) rows.push({ label: 'Motores', value: tractionMotors.join(', ') })
  if (configuration.transmissionId) rows.push({ label: 'Transmisión', value: 'Incluida' })
  if (charging.acCharging && recordOf(charging.acCharging).maxPowerKw !== undefined) rows.push({ label: 'Carga CA', value: `${formatNumber(String(recordOf(charging.acCharging).maxPowerKw))} kW` })
  if (charging.dcCharging && recordOf(charging.dcCharging).maxPowerKw !== undefined) rows.push({ label: 'Carga CC', value: `${formatNumber(String(recordOf(charging.dcCharging).maxPowerKw))} kW` })
  if (ports.length) rows.push({ label: 'Puertos', value: ports.join(', ') })

  return rows
}

function vehicleSafetyRows(item: ComparisonVehicle) {
  const safety = recordOf(item.vehicle.safety)
  const sections = [
    { title: 'Alertas de colisión', key: 'collisionWarnings', fields: { fcw: 'Alerta de colisión frontal', ldw: 'Alerta de salida de carril', bsw: 'Alerta de punto ciego', rctw: 'Alerta de tráfico cruzado trasero' } },
    { title: 'Intervención de colisión', key: 'collisionIntervention', fields: { aebCity: 'Frenado autónomo en ciudad', aebPedestrian: 'Frenado autónomo para peatones', aebHighway: 'Frenado autónomo en carretera', aebRear: 'Frenado autónomo trasero' } },
    { title: 'Asistencia a la conducción', key: 'drivingControlAssistance', fields: { lka: 'Asistencia de mantenimiento de carril', lca: 'Centrado de carril', acc: 'Control de crucero adaptativo', activeDrivingAssistanceDirectDriverMonitoring: 'Monitorización del conductor' } },
    { title: 'Seguridad y visibilidad', key: 'visibilityAndControl', fields: { drl: 'Luces diurnas', rearViewCamera: 'Cámara trasera', esc: 'Control electrónico de estabilidad', tractionControl: 'Control de tracción', abs: 'Frenos antibloqueo' } },
    { title: 'Seguridad trasera', key: 'rearSeatSafety', fields: { childSafety: 'Seguridad infantil', rearOccupantAlertEndOfTripReminder: 'Recordatorio de ocupante trasero' } },
    { title: 'Airbags', key: 'restraints', fields: { airbagSideFront: 'Airbags laterales delanteros', airbagSideRear: 'Airbags laterales traseros', headProtectionAirbag: 'Airbags de protección de cabeza' } }
  ]

  return sections.flatMap((section) => {
    const values = recordOf(safety[section.key])
    return Object.entries(section.fields).map(([field, feature]) => ({
      label: `${section.title} · ${feature}`,
      value: safetyValue(values[field])
    }))
  })
}

function climateRows(item: ComparisonVehicle) {
  const climate = recordOf(item.vehicle.climate)
  const rows: Array<{ label: string, value: string }> = []
  const features = {
    automaticClimateControl: 'Climatización automática',
    rearClimateControl: 'Climatización trasera',
    cabinAirFilter: 'Filtro de aire de cabina',
    airPurificationSystem: 'Sistema de purificación de aire',
    remotePreconditioning: 'Preacondicionamiento remoto',
    heatPump: 'Bomba de calor',
    heatedFrontSeats: 'Asientos delanteros calefactables',
    heatedRearSeats: 'Asientos traseros calefactables',
    heatedSteeringWheel: 'Volante calefactable'
  }

  if (climate.zoneCount !== undefined) {
    rows.push({ label: 'Zonas', value: String(climate.zoneCount) })
  }
  const measurements = {
    refrigerantType: 'Refrigerante',
    refrigerantGwp: 'GWP del refrigerante',
    compressorType: 'Tipo de compresor',
    coolingCapacity: 'Capacidad de enfriamiento',
    coolingPowerDraw: 'Potencia en enfriamiento',
    coolingCop: 'COP de enfriamiento',
    refrigerantCharge: 'Carga de refrigerante'
  }
  for (const [key, label] of Object.entries(measurements)) {
    if (climate[key] !== undefined) {
      rows.push({ label, value: measurement(climate[key]) })
    }
  }
  for (const [key, label] of Object.entries(features)) {
    if (climate[key] !== undefined) {
      rows.push({ label, value: climate[key] === true ? 'Disponible' : 'No disponible' })
    }
  }
  return rows
}

function safetyValue(value: unknown) {
  if (value === true) return 'Disponible'
  if (typeof value === 'number' && value > 0) return `${value} disponibles`
  return 'No disponible'
}

function recordOf(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {}
}

function itemsOf(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.map(recordOf) : []
}

function measurement(value: unknown) {
  const item = recordOf(value)
  if (item.widthMm !== undefined && item.aspectRatio !== undefined && item.rimDiameterInches !== undefined) {
    return `${formatNumber(String(item.widthMm))}/${formatNumber(String(item.aspectRatio))}R${formatNumber(String(item.rimDiameterInches))}`
  }
  return item.value !== undefined ? `${formatNumber(String(item.value))} ${item.unit ?? ''}`.trim() : String(value ?? missingValue)
}

function specificationLabel(value: string) {
  const labels: Record<string, string> = {
    length: 'Largo', width: 'Ancho', height: 'Alto', wheelbase: 'Distancia entre ejes', curbWeight: 'Peso del vehículo', trunkCapacity: 'Capacidad de la cajuela', cargoFloorWidthBetweenWheelHouses: 'Ancho del piso de carga entre pasos de rueda', frontCargoCapacity: 'Capacidad de carga frontal', maxCargoCapacitySeatsFolded: 'Capacidad de carga máx. con filas plegadas', doorCount: 'Puertas', passengerCapacity: 'Plazas', range: 'Autonomía', efficiency: 'Eficiencia', emissions: 'Emisiones', acceleration: 'Aceleración', topSpeed: 'Velocidad máxima', power: 'Potencia', torque: 'Par motor', frontBrakes: 'Frenos delanteros', rearBrakes: 'Frenos traseros', frontSuspension: 'Suspensión delantera', rearSuspension: 'Suspensión trasera', frontTire: 'Llantas delanteras', rearTire: 'Llantas traseras'
  }
  return labels[value] ?? value.replace(/([a-z])([A-Z])/g, '$1 $2')
}

function label(value: unknown) {
  const labels: Record<string, string> = {
    grid_electricity: 'Electricidad de red', gasoline: 'Gasolina', diesel: 'Diésel', battery_pack: 'Batería', fuel_tank: 'Depósito de combustible', combustion_engine: 'Motor de combustión', traction: 'Tracción', generator: 'Generador', front_axle: 'Eje delantero', rear_axle: 'Eje trasero', ac: 'CA', dc: 'CC', ac_dc: 'CA/CC'
  }
  return typeof value === 'string'
    ? powertrainArchitectureLabel(value) ?? labels[value] ?? value.replaceAll('_', ' ')
    : ''
}
</script>

<template>
  <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-sm font-medium text-muted-foreground">Catálogo</p>
        <h1 class="text-3xl font-bold tracking-tight">Comparar modelos</h1>
      </div>
      <Button as-child variant="outline">
        <NuxtLink to="/vehicles">Añadir vehículos</NuxtLink>
      </Button>
    </div>

    <Card v-if="comparison.count.value < 2">
      <CardContent class="flex flex-col items-start gap-3 p-6">
        <p class="text-sm text-muted-foreground">Selecciona al menos dos autos para compararlos.</p>
        <Button as-child><NuxtLink to="/vehicles">Explorar vehículos</NuxtLink></Button>
      </CardContent>
    </Card>

    <template v-else>
      <div class="overflow-x-auto rounded-md border">
        <table class="w-full min-w-[42rem] table-fixed border-collapse text-left text-sm">
          <colgroup>
            <col class="w-44">
            <col v-for="vehicle in selectedVehicles" :key="vehicle.id" class="w-52">
          </colgroup>
          <thead>
            <tr class="border-b bg-muted/40">
              <th class="w-36 p-3 font-medium text-muted-foreground">Características</th>
              <th v-for="vehicle in selectedVehicles" :key="vehicle.id" class="p-3 align-top">
                <div class="space-y-2">
                  <img v-if="vehicle.image" :src="vehicle.image.url" :alt="vehicle.image.alt" class="h-32 w-full rounded object-cover">
                  <div v-else class="flex h-32 w-full items-center justify-center rounded bg-muted text-muted-foreground">
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
            <template v-for="section in comparisonSections" :key="section.title">
              <tr class="border-y bg-muted/30">
                <th :colspan="comparison.selectedVehicles.value.length + 1" scope="colgroup" class="p-3 text-left font-semibold">{{ section.title }}</th>
              </tr>
              <tr v-for="row in section.rows" :key="`${section.title}-${row.label}`" class="border-b last:border-0">
                <th scope="row" class="p-3 font-medium text-muted-foreground">{{ row.label }}</th>
                <td v-for="(value, index) in row.values" :key="index" class="p-3">
                  <div v-if="section.title === 'Seguridad'" class="flex items-center gap-2">
                    <Icon
                      :name="value !== 'No disponible' ? 'tabler:check' : 'tabler:x'"
                      :class="value !== 'No disponible' ? 'size-4 shrink-0 text-emerald-500' : 'size-4 shrink-0 text-destructive'"
                      :aria-label="value !== 'No disponible' ? 'Disponible' : 'No disponible'"
                    />
                    <span>{{ value }}</span>
                  </div>
                  <div v-else-if="section.title === 'Evaluación NCAP'" class="space-y-1">
                    <template v-if="value">
                      <p class="font-medium">{{ safetyProgramLabel(value.program) }} {{ value.assessmentYear }}</p>
                      <div class="flex items-center gap-1" :aria-label="`${value.overallStars} de 5 estrellas`">
                        <Icon v-for="star in 5" :key="star" name="tabler:star-filled" :class="star <= value.overallStars ? 'size-4 text-amber-400' : 'size-4 text-muted'" aria-hidden="true" />
                        <span class="ml-1 text-xs tabular-nums">{{ value.overallStars }}/5</span>
                      </div>
                    </template>
                    <span v-else class="text-muted-foreground">No registrado</span>
                  </div>
                  <template v-else>{{ value }}</template>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

    </template>
  </section>
</template>