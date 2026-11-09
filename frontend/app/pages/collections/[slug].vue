<script setup lang="ts">
import { useQuery } from "@pinia/colada";
import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type {
  CatalogCollectionDetail,
  CatalogModel,
} from "#shared/types/catalog";

const route = useRoute();
const slug = computed(() => String(route.params.slug));
const { data: collection, status } = useQuery({
  key: () => ["collection", slug.value],
  query: () =>
    $fetch<CatalogCollectionDetail>(
      `/api/collections/${encodeURIComponent(slug.value)}`,
    ),
});

function modelForVehicle(
  vehicle: CatalogCollectionDetail["vehicles"][number]["vehicle"],
) {
  const lineage = vehicle.lineage;
  const image =
    vehicle.images?.leftSide ??
    vehicle.images?.silhouette ??
    vehicle.images?.front;

  return {
    id: lineage.modelId,
    makeId: lineage.makeId,
    makeName: lineage.makeName ?? "",
    modelName: lineage.modelName ?? "",
    makeSlug: lineage.makeSlug,
    generation:
      typeof lineage.generationId === "string" ? lineage.generationId : null,
    year: lineage.modelYear,
    baseBodyStyle: lineage.baseBodyStyle ?? null,
    ...(image ? { image } : {}),
  } satisfies Pick<CatalogModel, "id" | "makeId" | "makeName" | "modelName"> &
    Partial<
      Pick<
        CatalogModel,
        "makeSlug" | "generation" | "year" | "baseBodyStyle" | "image"
      >
    >;
}
</script>

<template>
  <section
    v-if="status === 'pending'"
    class="mx-auto w-full max-w-4xl space-y-6 px-4 py-8"
  >
    <Skeleton class="h-8 w-48" />
    <Skeleton class="h-24 w-full" />
    <Skeleton v-for="item in 3" :key="item" class="h-72" />
  </section>
  <section
    v-else-if="status === 'error'"
    class="mx-auto w-full max-w-4xl px-4 py-8"
  >
    <p role="alert" class="text-sm text-destructive">
      No se pudo cargar esta colección.
    </p>
  </section>
  <section
    v-else-if="collection"
    class="mx-auto w-full max-w-6xl space-y-8 px-4 py-8"
  >
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink as-child>
            <NuxtLink to="/collections">Colecciones</NuxtLink>
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>{{ collection.title }}</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <header class="space-y-4 border-b pb-6">
      <h1 class="text-3xl font-bold tracking-tight">{{ collection.title }}</h1>
      <p class="max-w-3xl text-muted-foreground">
        {{ collection.description }}
      </p>
      <Badge variant="secondary">
        {{ collection.vehicleCount }}
        {{ collection.vehicleCount === 1 ? "vehículo" : "vehículos" }}
      </Badge>
    </header>

    <div
      v-if="collection.vehicles.length"
      class="mx-auto w-full max-w-4xl space-y-6"
    >
      <div
        v-for="(item, index) in collection.vehicles"
        :key="item.vehicle.id"
        class="flex items-start gap-3 sm:gap-4"
      >
        <span
          class="w-8 shrink-0 pt-4 text-center text-2xl font-bold leading-none text-foreground"
          aria-hidden="true"
        >
          {{ index + 1 }}.
        </span>
        <div class="min-w-0 flex-1 space-y-4">
          <CatalogVehicleListingCard
            :model="modelForVehicle(item.vehicle)"
            :vehicle="item.vehicle"
            :index="index"
          />
          <p
            v-if="item.editorialNote"
            class="whitespace-pre-wrap text-sm leading-relaxed text-muted-foreground"
          >
            {{ item.editorialNote }}
          </p>
        </div>
      </div>
    </div>
    <Card v-else>
      <CardContent class="p-8 text-center text-sm text-muted-foreground">
        Esta colección todavía no tiene vehículos.
      </CardContent>
    </Card>
  </section>
</template>
