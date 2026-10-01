<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { refDebounced } from '@vueuse/core'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import type { ApiPage, CatalogRecall } from '#shared/types/catalog'

const route = useRoute()
const router = useRouter()
const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const requestedPage = Number.parseInt(typeof route.query.page === 'string' ? route.query.page : '', 10)
const page = ref(Number.isSafeInteger(requestedPage) && requestedPage > 0 ? requestedPage : 1)
const debouncedSearch = refDebounced(search, 300)
const recallQuery = computed(() => ({
  page: String(page.value),
  ...(debouncedSearch.value.trim() ? { q: debouncedSearch.value.trim() } : {})
}))
const { data, status } = useQuery({
  key: () => ['recalls', recallQuery.value],
  query: () => $fetch<ApiPage<CatalogRecall>>('/api/recalls', { query: recallQuery.value })
})
const pageCount = computed(() => Math.max(1, Math.ceil((data.value?.count ?? 0) / 10)))

watch(debouncedSearch, () => {
  page.value = 1
})

watch(recallQuery, (query) => {
  if (JSON.stringify(route.query) !== JSON.stringify(query)) {
    router.replace({ query })
  }
})

function formatDate(value: string | null) {
  if (!value) return 'Fecha no publicada'
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'long' }).format(new Date(`${value}T12:00:00`))
}
</script>

<template>
  <div>
    <section class="border-b bg-muted/30">
      <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
        <p class="text-sm font-medium text-muted-foreground">Seguridad</p>
        <h1 class="text-3xl font-bold tracking-tight">Recalls</h1>
      </div>
    </section>

    <section class="mx-auto w-full max-w-4xl space-y-8 px-4 py-8">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <label class="grid w-full max-w-md gap-2 text-sm font-medium">
          Buscar recalls
          <Input v-model="search" placeholder="Marca, modelo, número o título" />
        </label>
        <Badge variant="secondary" class="w-fit">{{ data?.count ?? 0 }} resultados</Badge>
      </div>

      <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">No se pudieron cargar los recalls. Revisa que la API esté disponible.</p>
      <div v-else-if="status === 'pending'" class="space-y-6">
        <Skeleton v-for="item in 3" :key="item" class="h-56" />
      </div>
      <div v-else-if="data?.results.length" class="relative space-y-8 before:absolute before:inset-y-0 before:left-3 before:w-px before:bg-border sm:before:left-4">
        <article v-for="recall in data.results" :key="recall.id" class="relative pl-10 sm:pl-12">
          <span class="absolute left-0 top-7 flex size-7 items-center justify-center rounded-full border-4 border-background bg-destructive sm:left-1" aria-hidden="true">
            <Icon name="tabler:alert-triangle" class="size-4 text-destructive-foreground" />
          </span>
          <Card>
            <CardHeader class="space-y-3">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <CardDescription>{{ formatDate(recall.publishedDate) }}</CardDescription>
                <Badge :variant="recall.status === 'resolved' ? 'secondary' : 'destructive'">{{ recall.status === 'resolved' ? 'Resuelto' : 'Abierto' }}</Badge>
              </div>
              <CardTitle>{{ recall.title }}</CardTitle>
              <CardDescription>{{ recall.makerName }} · {{ recall.recallNumber }}</CardDescription>
            </CardHeader>
            <CardContent class="space-y-4 text-sm">
              <p v-if="recall.description">{{ recall.description }}</p>
              <dl class="grid gap-4 sm:grid-cols-2">
                <div v-if="recall.risk" class="space-y-1"><dt class="font-medium">Riesgo</dt><dd class="text-muted-foreground">{{ recall.risk }}</dd></div>
                <div v-if="recall.riskConsequence" class="space-y-1"><dt class="font-medium">Consecuencia del riesgo</dt><dd class="text-muted-foreground">{{ recall.riskConsequence }}</dd></div>
                <div v-if="recall.countermeasure" class="space-y-1"><dt class="font-medium">Medida correctiva</dt><dd class="text-muted-foreground">{{ recall.countermeasure }}</dd></div>
                <div v-if="recall.actions" class="space-y-1"><dt class="font-medium">Acciones requeridas</dt><dd class="text-muted-foreground">{{ recall.actions }}</dd></div>
                <div v-if="recall.damageReport" class="space-y-1"><dt class="font-medium">Reporte de daños</dt><dd class="text-muted-foreground">{{ recall.damageReport }}</dd></div>
                <div v-if="recall.totalUnitsAffected !== null" class="space-y-1"><dt class="font-medium">Unidades afectadas</dt><dd class="text-muted-foreground">{{ recall.totalUnitsAffected.toLocaleString('es-MX') }}</dd></div>
                <div v-if="recall.affectedModels.length" class="space-y-1"><dt class="font-medium">Modelos afectados</dt><dd class="flex flex-wrap gap-2"><NuxtLink v-for="model in recall.affectedModels" :key="model.id" :to="`/models/${model.id}`" class="underline underline-offset-4">{{ model.name }} {{ model.year }}</NuxtLink></dd></div>
              </dl>
              <a v-if="recall.sourceUrl" :href="recall.sourceUrl" target="_blank" rel="noreferrer" class="inline-flex items-center gap-1 font-medium underline underline-offset-4">Ver fuente <Icon name="tabler:external-link" class="size-4" aria-hidden="true" /></a>
            </CardContent>
          </Card>
        </article>
      </div>
      <Card v-else>
        <CardContent class="flex flex-col items-center gap-2 p-8 text-center">
          <Icon name="tabler:search-off" class="size-8 text-muted-foreground" aria-hidden="true" />
          <h2 class="font-semibold">No hay recalls para mostrar</h2>
          <p class="text-sm text-muted-foreground">Prueba con otra búsqueda.</p>
        </CardContent>
      </Card>

      <nav v-if="pageCount > 1" class="flex items-center justify-center gap-3" aria-label="Paginación de recalls">
        <Button type="button" variant="outline" size="icon" :disabled="!data?.previous" aria-label="Página anterior" title="Página anterior" @click="page--"><Icon name="tabler:chevron-left" class="size-4" aria-hidden="true" /></Button>
        <span class="text-sm text-muted-foreground">Página {{ page }} de {{ pageCount }}</span>
        <Button type="button" variant="outline" size="icon" :disabled="!data?.next" aria-label="Página siguiente" title="Página siguiente" @click="page++"><Icon name="tabler:chevron-right" class="size-4" aria-hidden="true" /></Button>
      </nav>
    </section>
  </div>
</template>