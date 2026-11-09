<script setup lang="ts">
import { useQuery } from "@pinia/colada";
import { refDebounced } from "@vueuse/core";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { NativeSelect, NativeSelectOption } from "@/components/ui/native-select";
import { Skeleton } from "@/components/ui/skeleton";
import type { ApiPage, CatalogMake, CommercialModel } from "#shared/types/catalog";

const route = useRoute();
const router = useRouter();

function queryValue(name: string) {
  const value = route.query[name];
  return typeof value === "string" ? value : "";
}

const search = ref(queryValue("q"));
const make = ref(queryValue("make") || "all");
const requestedPage = Number.parseInt(queryValue("page"), 10);
const page = ref(
  Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1,
);
const debouncedSearch = refDebounced(search, 300);
const catalogQuery = computed(() => ({
  page: String(page.value),
  ...(debouncedSearch.value.trim() ? { q: debouncedSearch.value.trim() } : {}),
  ...(make.value !== "all" ? { make: make.value } : {}),
}));

const { data, status } = useQuery({
  key: () => ["commercial-models", catalogQuery.value],
  query: () =>
    $fetch<ApiPage<CommercialModel>>("/api/model-commercial", {
      query: catalogQuery.value,
    }),
});
const { data: makes, status: makesStatus } = useQuery({
  key: ["makes"],
  query: () => $fetch<ApiPage<CatalogMake>>("/api/makes"),
});
const pageCount = computed(() =>
  Math.max(1, Math.ceil((data.value?.count ?? 0) / 12)),
);

watch([debouncedSearch, make], () => {
  page.value = 1;
});
watch(catalogQuery, (query) => {
  if (JSON.stringify(route.query) !== JSON.stringify(query)) {
    router.replace({ query });
  }
});

function resetFilters() {
  search.value = "";
  make.value = "all";
  page.value = 1;
}

function yearLabel(model: CommercialModel) {
  if (model.startYear === null || model.endYear === null) return null;
  return model.startYear === model.endYear
    ? String(model.startYear)
    : `${model.startYear} - ${model.endYear}`;
}
</script>

<template>
  <div>
    <section class="border-b bg-muted/30">
      <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
        <p class="text-sm font-medium text-muted-foreground">Explorar</p>
        <h1 class="text-3xl font-bold tracking-tight">Catálogo de autos</h1>
      </div>
    </section>

    <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
      <Card>
        <CardContent class="grid grid-cols-1 gap-4 p-4 sm:p-6 md:grid-cols-3 md:items-end">
          <label class="grid gap-2 text-sm font-medium">
            Buscar
            <Input v-model="search" placeholder="Modelo" />
          </label>
          <label class="grid gap-2 text-sm font-medium">
            Marca
            <NativeSelect v-model="make" class="w-full" aria-label="Filtrar por marca">
              <NativeSelectOption value="all">Todas las marcas</NativeSelectOption>
              <NativeSelectOption
                v-for="item in makes?.results"
                :key="item.id"
                :value="item.id"
              >{{ item.name }}</NativeSelectOption>
            </NativeSelect>
          </label>
          <Button type="button" variant="outline" @click="resetFilters">Limpiar</Button>
        </CardContent>
      </Card>

      <div class="flex items-center justify-between gap-4">
        <h2 class="text-lg font-semibold tracking-tight">Modelos comerciales</h2>
        <Badge variant="secondary">{{ data?.count ?? 0 }} resultados</Badge>
      </div>
      <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">
        No se pudo cargar el catálogo. Revisa que la API esté disponible.
      </p>
      <p v-if="makesStatus === 'error'" role="alert" class="text-sm text-destructive">
        No se pudieron cargar las marcas. Revisa que la API esté disponible.
      </p>
      <div v-if="status === 'pending'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Skeleton v-for="item in 6" :key="item" class="h-40" />
      </div>
      <div
        v-else-if="status !== 'error' && data?.results.length"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        <Card v-for="model in data.results" :key="model.id" class="h-full transition-shadow hover:shadow-md">
          <CardHeader>
            <CardTitle>
              <NuxtLink
                :to="`/makes/${encodeURIComponent(model.makeSlug)}/models/${encodeURIComponent(model.name)}`"
                class="transition-colors hover:text-muted-foreground"
              >{{ model.name }}</NuxtLink>
            </CardTitle>
            <CardDescription>
              <NuxtLink :to="`/makes/${encodeURIComponent(model.makeSlug)}`" class="hover:text-foreground">
                {{ model.makeName }}
              </NuxtLink>
            </CardDescription>
          </CardHeader>
          <CardContent class="flex flex-wrap gap-2">
            <Badge variant="secondary">
              {{ model.generationCount }} {{ model.generationCount === 1 ? "generación" : "generaciones" }}
            </Badge>
            <Badge v-if="yearLabel(model)" variant="outline">{{ yearLabel(model) }}</Badge>
          </CardContent>
        </Card>
      </div>
      <Card v-else-if="status !== 'error'">
        <CardContent class="flex flex-col items-center gap-2 p-8 text-center">
          <Icon name="tabler:car-off" class="size-8 text-muted-foreground" aria-hidden="true" />
          <h3 class="font-semibold">No hay modelos para mostrar</h3>
          <p class="text-sm text-muted-foreground">Prueba a cambiar los filtros o vuelve más tarde.</p>
        </CardContent>
      </Card>
      <nav v-if="pageCount > 1" class="flex items-center justify-center gap-3" aria-label="Paginación">
        <Button
          type="button" variant="outline" size="icon" :disabled="!data?.previous"
          aria-label="Página anterior" @click="page--"
        >
          <Icon name="tabler:chevron-left" class="size-4" aria-hidden="true" />
        </Button>
        <span class="text-sm text-muted-foreground">Página {{ page }} de {{ pageCount }}</span>
        <Button
          type="button" variant="outline" size="icon" :disabled="!data?.next"
          aria-label="Página siguiente" @click="page++"
        >
          <Icon name="tabler:chevron-right" class="size-4" aria-hidden="true" />
        </Button>
      </nav>
    </section>
  </div>
</template>
