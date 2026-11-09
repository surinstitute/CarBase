<script setup lang="ts">
import { useQuery } from "@pinia/colada";
import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { ApiPage, CatalogCollection } from "#shared/types/catalog";

const { data, status } = useQuery({
  key: ["collections"],
  query: () => $fetch<ApiPage<CatalogCollection>>("/api/collections"),
});
</script>

<template>
  <div>
    <section class="border-b bg-muted/30">
      <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
        <p class="text-sm font-medium text-muted-foreground">Explorar</p>
        <h1 class="text-3xl font-bold tracking-tight">Colecciones</h1>
        <p class="max-w-2xl text-muted-foreground">
          Selecciones de vehículos organizadas por tema y recomendación.
        </p>
      </div>
    </section>

    <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbPage>Colecciones</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <p
        v-if="status === 'error'"
        role="alert"
        class="text-sm text-destructive"
      >
        No se pudieron cargar las colecciones.
      </p>
      <div
        v-else-if="status === 'pending'"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <Skeleton v-for="item in 6" :key="item" class="h-48" />
      </div>
      <div
        v-else-if="data?.results.length"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <Card
          v-for="collection in data.results"
          :key="collection.id"
          class="h-full transition-shadow hover:shadow-md"
        >
          <CardHeader>
            <CardTitle>
              <NuxtLink
                :to="`/collections/${encodeURIComponent(collection.slug)}`"
                class="hover:underline underline-offset-4"
              >{{ collection.title }}</NuxtLink>
            </CardTitle>
            <CardDescription>{{ collection.description }}</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="secondary">
              {{ collection.vehicleCount }}
              {{ collection.vehicleCount === 1 ? "vehículo" : "vehículos" }}
            </Badge>
          </CardContent>
        </Card>
      </div>
      <Card v-else>
        <CardContent class="p-8 text-center text-sm text-muted-foreground">
          Todavía no hay colecciones publicadas.
        </CardContent>
      </Card>
    </section>
  </div>
</template>
