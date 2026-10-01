<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { countryFlag, formatNumber } from '@/lib/utils'
import type { CatalogResponse } from '#shared/types/catalog'

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
const specs = computed(() => recordOf(variant.value?.specs))
const performance = computed(() => recordOf(variant.value?.performance))
const configuration = computed(() => recordOf(variant.value?.configuration))
const specRows = computed(() => Object.entries(specs.value).map(([field, value]) => ({
  field: fieldLabel(field),
  value: measurement(value)
})))
const performanceSections = computed(() => Object.entries(performance.value)
  .map(([field, value]) => ({ field: fieldLabel(field), rows: performanceRows(value) }))
  .filter((section) => section.rows.length))
const configurationRows = computed(() => {
  const powertrain = recordOf(configuration.value.powertrain)
  const charging = recordOf(configuration.value.charging)
  const rows: Array<{ field: string, value: string }> = []
  const energySources = itemsOf(powertrain.energySources).map((item) => label(item.source)).filter(Boolean)
  const energyStorage = itemsOf(powertrain.energyStorage).map((item) => [
    label(item.type),
    item.capacityKwh !== undefined ? `${formatNumber(String(item.capacityKwh))} kWh` : ''
  ].filter(Boolean).join(' · ')).filter(Boolean)
  const energyConverters = itemsOf(powertrain.energyConverters).map((item) => label(item.type)).filter(Boolean)
  const tractionMotors = itemsOf(powertrain.tractionMotors).map((item) => [label(item.role), label(item.position), item.quantity ? `x${formatNumber(String(item.quantity))}` : ''].filter(Boolean).join(' · ')).filter(Boolean)
  const acCharging = recordOf(charging.acCharging)
  const dcCharging = recordOf(charging.dcCharging)
  const ports = itemsOf(charging.ports).map((item) => [label(item.currentType), label(item.connector), label(item.location)].filter(Boolean).join(' · ')).filter(Boolean)

  if (powertrain.architecture) rows.push({ field: 'Propulsión', value: label(powertrain.architecture) })
  if (energySources.length) rows.push({ field: 'Fuente de energía', value: energySources.join(', ') })
  if (energyStorage.length) rows.push({ field: 'Almacenamiento', value: energyStorage.join(', ') })
  if (energyConverters.length) rows.push({ field: 'Convertidores', value: energyConverters.join(', ') })
  if (tractionMotors.length) rows.push({ field: 'Motores', value: tractionMotors.join(', ') })
  if (configuration.value.transmissionId) rows.push({ field: 'Transmisión', value: 'Incluida' })
  if (acCharging.maxPowerKw !== undefined) rows.push({ field: 'Carga CA', value: `${formatNumber(String(acCharging.maxPowerKw))} kW` })
  if (dcCharging.maxPowerKw !== undefined) rows.push({ field: 'Carga CC', value: `${formatNumber(String(dcCharging.maxPowerKw))} kW` })
  if (ports.length) rows.push({ field: 'Puertos', value: ports.join(', ') })

  return rows
})
const labels: Record<string, string> = {
  battery_electric: 'Eléctrico de batería',
  bev: 'Eléctrico de batería',
  ice: 'Combustión interna',
  mild_hybrid: 'Mild hybrid',
  series_hybrid: 'Híbrido serie',
  parallel_hybrid: 'Híbrido paralelo',
  power_split_hybrid: 'Híbrido combinado',
  phev: 'Híbrido enchufable',
  plug_in_hybrid: 'Híbrido enchufable',
  fcev: 'Pila de combustible',
  fuel_cell_electric: 'Pila de combustible',
  grid_electricity: 'Electricidad de red',
  gasoline: 'Gasolina',
  diesel: 'Diésel',
  e85: 'E85',
  cng: 'Gas natural comprimido',
  lpg: 'Gas licuado de petróleo',
  hydrogen: 'Hidrógeno',
  battery_pack: 'Batería',
  fuel_tank: 'Depósito de combustible',
  combustion_engine: 'Motor de combustión',
  traction: 'Tracción',
  generator: 'Generador',
  front_axle: 'Eje delantero',
  rear_axle: 'Eje trasero',
  front_left: 'Delante izquierda',
  front_right: 'Delante derecha',
  rear_left: 'Detrás izquierda',
  rear_right: 'Detrás derecha',
  center: 'Centro',
  total_range: 'Autonomía total',
  electric_range: 'Autonomía eléctrica',
  fuel_consumption: 'Consumo de combustible',
  energy_consumption: 'Consumo de energía',
  fuel_economy: 'Rendimiento',
  co2_tailpipe: 'CO2 en escape',
  co2_weighted: 'CO2 ponderado',
  '0_100_kmh': '0-100 km/h',
  '0_60_mph': '0-60 mph',
  '0_200_kmh': '0-200 km/h',
  quarter_mile: 'Cuarto de milla',
  electric_motor_power: 'Potencia eléctrica',
  combustion_engine_power: 'Potencia de combustión',
  peak_torque: 'Par máximo',
  system_torque: 'Par del sistema',
  wltp: 'WLTP',
  epa: 'EPA',
  ftp: 'FTP',
  hfet: 'HFET',
  nedc: 'NEDC',
  cltc: 'CLTC',
  jc08: 'JC08',
  city: 'Ciudad',
  highway: 'Carretera',
  combined: 'Combinado',
  mixed: 'Mixto',
  km_h: 'km/h',
  g_per_km: 'g/km',
  mg_per_km: 'mg/km',
  number_per_km: 'número/km',
  g_per_pba: 'g/PBA',
  kw: 'kW',
  nm: 'Nm',
  lb_ft: 'lb-ft',
  l_per_100km: 'L/100 km',
  kg_per_100km: 'kg/100 km',
  kwh_per_100km: 'kWh/100 km',
  wh_per_km: 'Wh/km',
  mpg_us: 'mpg US',
  mpg_imp: 'mpg imp',
  km_per_l: 'km/L',
  km_per_kg: 'km/kg',
  ac: 'CA',
  dc: 'CC',
  ac_dc: 'CA/CC'
}

function formatValue(value: unknown) {
  if (value === null) return 'null'
  if (typeof value === 'object') return JSON.stringify(value, null, 2) ?? ''
  return String(value)
}

function recordOf(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {}
}

function itemsOf(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.map(recordOf) : []
}

function label(value: unknown) {
  if (typeof value !== 'string') return ''
  return labels[value] ?? value.replaceAll('_', ' ')
}

function fieldLabel(value: string) {
  const fieldLabels: Record<string, string> = {
    length: 'Largo',
    width: 'Ancho',
    height: 'Alto',
    wheelbase: 'Distancia entre ejes',
    curbWeight: 'Peso del vehículo',
    trunkCapacity: 'Capacidad de la cajuela',
    doorCount: 'Puertas',
    passengerCapacity: 'Plazas',
    range: 'Autonomía',
    efficiency: 'Eficiencia',
    emissions: 'Emisiones',
    acceleration: 'Aceleración',
    topSpeed: 'Velocidad máxima',
    power: 'Potencia',
    torque: 'Par motor',
    frontBrakes: 'Frenos delanteros',
    rearBrakes: 'Frenos traseros',
    frontSuspension: 'Suspensión delantera',
    rearSuspension: 'Suspensión trasera',
    frontTire: 'Llantas delanteras',
    rearTire: 'Llantas traseras'
  }
  return fieldLabels[value] ?? value.replace(/([a-z])([A-Z])/g, '$1 $2')
}

function measurement(value: unknown) {
  const item = recordOf(value)
  if (item.widthMm !== undefined && item.aspectRatio !== undefined && item.rimDiameterInches !== undefined) {
    return `${formatNumber(String(item.widthMm))}/${formatNumber(String(item.aspectRatio))}R${formatNumber(String(item.rimDiameterInches))}`
  }
  return item.value !== undefined ? `${formatNumber(String(item.value))} ${item.unit ?? ''}`.trim() : formatValue(value)
}

function performanceRows(value: unknown) {
  return itemsOf(value).map((item) => ({
    label: label(item.metric) || 'Resultado',
    value: `${formatNumber(String(item.value)) || '—'} ${label(item.unit) || item.unit || ''}`.trim(),
    detail: [label(item.cycle), label(item.scope)].filter(Boolean).join(' · ')
  }))
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
            <template v-if="variant.assemblyCountry">
              <dt class="text-muted-foreground">País de armado</dt><dd class="font-medium">{{ countryFlag(String(variant.assemblyCountry)) }} {{ variant.assemblyCountry }}</dd>
            </template>
          </dl>
        </CardContent>
      </Card>
    </div>

    <div class="grid gap-6 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>Especificaciones</CardTitle>
          <CardDescription>Dimensiones y capacidad.</CardDescription>
        </CardHeader>
        <CardContent>
          <dl v-if="specRows.length" class="space-y-3 text-sm">
            <div v-for="row in specRows" :key="row.field" class="flex items-baseline justify-between gap-4 border-b pb-3 last:border-0 last:pb-0">
              <dt class="text-muted-foreground">{{ row.field }}</dt>
              <dd class="text-right font-medium">{{ row.value }}</dd>
            </div>
          </dl>
          <p v-else class="text-sm text-muted-foreground">No hay especificaciones disponibles.</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Rendimiento</CardTitle>
          <CardDescription>Mediciones declaradas para esta variante.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-5">
          <div v-for="section in performanceSections" :key="section.field" class="space-y-2">
            <h3 class="text-sm font-medium">{{ section.field }}</h3>
            <dl class="space-y-2 text-sm">
              <div v-for="row in section.rows" :key="`${row.label}-${row.value}`" class="grid grid-cols-[1fr_auto] gap-x-3">
                <dt class="text-muted-foreground">{{ row.label }}<span v-if="row.detail"> · {{ row.detail }}</span></dt>
                <dd class="font-medium">{{ row.value }}</dd>
              </div>
            </dl>
          </div>
          <p v-if="!performanceSections.length" class="text-sm text-muted-foreground">No hay mediciones de rendimiento disponibles.</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Configuración</CardTitle>
          <CardDescription>Propulsión, almacenamiento y carga.</CardDescription>
        </CardHeader>
        <CardContent>
          <dl v-if="configurationRows.length" class="space-y-3 text-sm">
            <div v-for="row in configurationRows" :key="row.field" class="space-y-1 border-b pb-3 last:border-0 last:pb-0">
              <dt class="text-muted-foreground">{{ row.field }}</dt>
              <dd class="font-medium">{{ row.value }}</dd>
            </div>
          </dl>
          <p v-else class="text-sm text-muted-foreground">No hay datos de configuración disponibles.</p>
        </CardContent>
      </Card>
    </div>

    <CatalogSafetyPackage :safety="variant.safety" />

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