<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { CatalogVehicleRecord } from '#shared/types/catalog'

const props = withDefaults(defineProps<{
  safety: CatalogVehicleRecord['safety']
  title?: string
  description?: string
}>(), {
  title: 'Seguridad',
  description: 'Sistemas de alerta, asistencia y protección de esta variante.'
})

const safetySections = [
  {
    title: 'Alertas de colisión',
    fields: {
      fcw: 'Alerta de colisión frontal',
      ldw: 'Alerta de salida de carril',
      bsw: 'Alerta de punto ciego',
      rctw: 'Alerta de tráfico cruzado trasero'
    }
  },
  {
    title: 'Intervención de colisión',
    fields: {
      aebCity: 'Frenado autónomo en ciudad',
      aebPedestrian: 'Frenado autónomo para peatones',
      aebHighway: 'Frenado autónomo en carretera',
      aebRear: 'Frenado autónomo trasero'
    }
  },
  {
    title: 'Asistencia a la conducción',
    fields: {
      lka: 'Asistencia de mantenimiento de carril',
      lca: 'Centrado de carril',
      acc: 'Control de crucero adaptativo',
      activeDrivingAssistanceDirectDriverMonitoring: 'Monitorización del conductor'
    }
  },
  {
    title: 'Seguridad y visibilidad',
    fields: {
      drl: 'Luces diurnas',
      rearViewCamera: 'Cámara trasera',
      esc: 'Control electrónico de estabilidad',
      tractionControl: 'Control de tracción',
      abs: 'Frenos antibloqueo'
    }
  },
  {
    title: 'Seguridad trasera',
    fields: {
      childSafety: 'Seguridad infantil',
      rearOccupantAlertEndOfTripReminder: 'Recordatorio de ocupante trasero'
    }
  },
  {
    title: 'Airbags',
    fields: {
      airbagSideFront: 'Airbags laterales delanteros',
      airbagSideRear: 'Airbags laterales traseros',
      headProtectionAirbag: 'Airbags de protección de cabeza'
    }
  }
] as const

const detailSafetySections = computed(() => safetySections.map((section) => ({
  title: section.title,
  values: safetyRows(props.safety?.[sectionKey(section.title)], section.fields)
})))

function sectionKey(title: typeof safetySections[number]['title']) {
  const keys = {
    'Alertas de colisión': 'collisionWarnings',
    'Intervención de colisión': 'collisionIntervention',
    'Asistencia a la conducción': 'drivingControlAssistance',
    'Seguridad y visibilidad': 'visibilityAndControl',
    'Seguridad trasera': 'rearSeatSafety',
    Airbags: 'restraints'
  } as const
  return keys[title]
}

function safetyRows(value: unknown, fields: Record<string, string>) {
  const section = value && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {}

  return Object.entries(fields).map(([field, label]) => ({
    label,
    value: section[field],
    present: section[field] === true || (typeof section[field] === 'number' && section[field] > 0)
  }))
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ title }}</CardTitle>
      <CardDescription>{{ description }}</CardDescription>
    </CardHeader>
    <CardContent>
      <div v-if="safety" class="grid gap-x-8 gap-y-6 md:grid-cols-2 lg:grid-cols-3">
        <section v-for="section in detailSafetySections" :key="section.title" class="space-y-3">
          <h3 class="text-sm font-medium">{{ section.title }}</h3>
          <ul class="space-y-2 text-sm">
            <li v-for="feature in section.values" :key="feature.label" class="flex items-start gap-2">
              <Icon :name="feature.present ? 'tabler:check' : 'tabler:x'" :class="feature.present ? 'mt-0.5 size-4 shrink-0 text-emerald-500' : 'mt-0.5 size-4 shrink-0 text-destructive'" :aria-label="feature.present ? 'Disponible' : 'No disponible'" />
              <span :class="feature.present ? 'text-foreground' : 'text-muted-foreground'">{{ feature.label }}<template v-if="typeof feature.value === 'number'">: {{ feature.value }}</template></span>
            </li>
          </ul>
        </section>
      </div>
      <p v-else class="text-sm text-muted-foreground">No hay paquete de seguridad registrado para esta variante.</p>
    </CardContent>
  </Card>
</template>