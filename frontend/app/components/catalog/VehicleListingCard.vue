<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { variantPath, vehicleIdPath } from "@/lib/model-path";
import { powertrainArchitectureLabel } from "@/lib/powertrain";
import { formatNumber } from "@/lib/utils";
import type { CatalogModel, CatalogVehicleRecord } from "#shared/types/catalog";

type ListingCardModel = Pick<
  CatalogModel,
  "id" | "makeId" | "makeName" | "modelName"
> &
  Partial<
    Pick<CatalogModel, "makeSlug" | "generation" | "year" | "baseBodyStyle" | "image">
  >;

const props = defineProps<{
  model: ListingCardModel;
  vehicle: CatalogVehicleRecord;
  index?: number;
}>();

const comparison = useCarComparison();
const image = computed(
  () =>
    props.vehicle.images?.leftSide ??
    props.vehicle.images?.silhouette ??
    props.vehicle.images?.front ??
    props.model.image,
);
const isSelected = computed(() =>
  comparison.selectedVehicles.value.some(
    (selected) => selected.id === String(props.vehicle.id),
  ),
);
const vehiclePath = computed(() => {
  if (!props.model.makeSlug || !props.model.year) {
    return vehicleIdPath(props.model.id, props.vehicle.id);
  }

  return variantPath(
    {
      makeSlug: props.model.makeSlug,
      modelName: props.model.modelName,
      generation: props.model.generation ?? null,
      year: props.model.year,
      baseBodyStyle: props.model.baseBodyStyle ?? null,
    },
    props.vehicle.variantName,
    props.vehicle.id,
  );
});
const variantLabel = computed(
  () => props.vehicle.variantName || `Variante ${(props.index ?? 0) + 1}`,
);
const powertrainArchitecture = computed(
  () => props.vehicle.configuration.powertrain?.architecture,
);
const architectureLabel = computed(() =>
  powertrainArchitecture.value
    ? powertrainArchitectureLabel(powertrainArchitecture.value) ??
      powertrainArchitecture.value.replaceAll("_", " ")
    : null,
);
</script>

<template>
  <Card
    class="gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md md:flex-row"
  >
    <NuxtLink
      :to="vehiclePath"
      class="flex aspect-2/1 w-full shrink-0 items-center justify-center overflow-hidden bg-muted text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring md:aspect-auto md:min-h-56 md:w-64"
    >
      <img
        v-if="image"
        :src="image.url"
        :alt="image.alt"
        class="h-full w-full object-cover"
      >
      <Icon v-else name="tabler:car" class="size-12" aria-hidden="true" />
    </NuxtLink>
    <div class="flex min-w-0 flex-1 flex-col justify-between gap-5 p-5 md:p-6">
      <div class="space-y-4">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 space-y-1">
            <p class="text-sm text-muted-foreground">
              {{ model.makeName }} {{ model.modelName }}
            </p>
            <h2 class="text-lg font-semibold">
              <NuxtLink :to="vehiclePath" class="underline underline-offset-4">
                {{ variantLabel }}
              </NuxtLink>
            </h2>
          </div>
          <div class="flex shrink-0 items-center gap-2">
            <Badge variant="secondary">{{ vehicle.lineage.modelYear }}</Badge>
            <Button
              type="button"
              variant="outline"
              size="icon"
              class="size-9 rounded-full"
              :aria-label="
                isSelected
                  ? `Quitar ${variantLabel} de comparación`
                  : `Añadir ${variantLabel} a comparación`
              "
              :title="
                isSelected
                  ? 'Quitar de comparación'
                  : comparison.isAtLimit.value
                    ? 'Máximo de 4 autos seleccionados'
                    : 'Añadir a comparación'
              "
              :aria-pressed="isSelected"
              :disabled="!isSelected && comparison.isAtLimit.value"
              @click="comparison.toggle(model, vehicle)"
            >
              <Icon
                :name="isSelected ? 'tabler:minus' : 'tabler:plus'"
                class="size-4"
                aria-hidden="true"
              />
            </Button>
          </div>
        </div>

      </div>

      <div class="flex flex-wrap gap-2">
        <Badge
          v-if="vehicle.lineage.generationId"
          variant="outline"
        >
          {{ vehicle.lineage.generationId }}
        </Badge>
        <Badge
          v-if="vehicle.configuration.bodyStyle"
          variant="outline"
        >
          {{ vehicle.configuration.bodyStyle }}
        </Badge>
        <Badge v-if="architectureLabel" variant="outline">
          {{ architectureLabel }}
        </Badge>
        <Badge v-if="vehicle.priceAmount" variant="outline">
          {{ vehicle.priceCurrency }} {{ formatNumber(vehicle.priceAmount) }}
        </Badge>
      </div>
    </div>
  </Card>
</template>
