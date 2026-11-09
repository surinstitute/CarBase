<script setup lang="ts">
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { safetySections } from "#shared/safety";
import type { CatalogVehicleRecord } from "#shared/types/catalog";

const props = withDefaults(
  defineProps<{
    safety: CatalogVehicleRecord["safety"];
    title?: string;
    description?: string;
  }>(),
  {
    title: "Seguridad",
    description:
      "Sistemas de alerta, asistencia y protección de esta variante.",
  },
);

const detailSafetySections = computed(() =>
  safetySections.map((section) => ({
    title: section.title,
    values: safetyRows(props.safety?.[section.key], section.fields),
  })),
);

function safetyRows(
  value: unknown,
  fields: readonly { key: string; label: string }[],
) {
  const section =
    value && typeof value === "object" && !Array.isArray(value)
      ? (value as Record<string, unknown>)
      : {};

  return fields.map(({ key, label }) => ({
    label,
    value: section[key],
    present:
      section[key] === true ||
      (typeof section[key] === "number" && section[key] > 0),
  }));
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ title }}</CardTitle>
      <CardDescription>{{ description }}</CardDescription>
    </CardHeader>
    <CardContent>
      <div
        v-if="safety"
        class="grid gap-x-8 gap-y-6 md:grid-cols-2 lg:grid-cols-3"
      >
        <section
          v-for="section in detailSafetySections"
          :key="section.title"
          class="space-y-3"
        >
          <h3 class="text-sm font-medium">{{ section.title }}</h3>
          <ul class="space-y-2 text-sm">
            <li
              v-for="feature in section.values"
              :key="feature.label"
              class="flex items-start gap-2"
            >
              <Icon
                :name="feature.present ? 'tabler:check' : 'tabler:x'"
                :class="
                  feature.present
                    ? 'mt-0.5 size-4 shrink-0 text-emerald-500'
                    : 'mt-0.5 size-4 shrink-0 text-destructive'
                "
                :aria-label="feature.present ? 'Disponible' : 'No disponible'"
              />
              <span
                :class="
                  feature.present ? 'text-foreground' : 'text-muted-foreground'
                "
                >{{ feature.label
                }}<template v-if="typeof feature.value === 'number'"
                  >: {{ feature.value }}</template
                ></span
              >
            </li>
          </ul>
        </section>
      </div>
      <p v-else class="text-sm text-muted-foreground">
        No hay paquete de seguridad registrado para esta variante.
      </p>
    </CardContent>
  </Card>
</template>
