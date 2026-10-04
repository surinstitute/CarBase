<script setup lang="ts">
import { useQuery } from '@pinia/colada'
import { Badge } from '@/components/ui/badge'
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import type { ApiPage, CatalogGroup } from '#shared/types/catalog'

const search = ref('')
const { data: groups, status: groupsStatus } = useQuery({
  key: ['groups'],
  query: () => $fetch<ApiPage<CatalogGroup>>('/api/groups')
})
const status = computed(() => (
  groupsStatus.value === 'error'
    ? 'error'
    : groupsStatus.value === 'pending'
      ? 'pending'
      : 'success'
))
const filteredGroups = computed(() => {
  const term = search.value.trim().toLocaleLowerCase()
  return (groups.value?.results ?? [])
    .filter((group) => group.name.toLocaleLowerCase().includes(term))
    .sort((first, second) => first.name.localeCompare(second.name))
})

</script>

<template>
  <section class="border-b bg-muted/30">
    <div class="mx-auto w-full max-w-6xl space-y-2 px-4 py-10">
      <p class="text-sm font-medium text-muted-foreground">Explorar</p>
      <h1 class="text-3xl font-bold tracking-tight">Grupos automotrices</h1>
    </div>
  </section>

  <section class="mx-auto w-full max-w-6xl space-y-6 px-4 py-8">
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem><BreadcrumbLink as-child><NuxtLink to="/models">Modelos</NuxtLink></BreadcrumbLink></BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem><BreadcrumbPage>Grupos</BreadcrumbPage></BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>

    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <label class="grid w-full gap-2 text-sm font-medium sm:max-w-sm">
        Buscar grupo
        <Input v-model="search" placeholder="Nombre del grupo" />
      </label>
      <Badge variant="secondary">{{ filteredGroups.length }} grupos</Badge>
    </div>

    <div class="flex items-center justify-between gap-4">
      <h2 class="text-lg font-semibold">Todos los grupos</h2>
    </div>
    <p v-if="status === 'error'" role="alert" class="text-sm text-destructive">No se pudo cargar la lista de grupos.</p>
    <div v-else-if="status === 'pending'" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Skeleton v-for="item in 6" :key="item" class="h-36" />
    </div>
    <div v-else-if="filteredGroups.length" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card v-for="group in filteredGroups" :key="group.id" class="transition-shadow hover:shadow-md">
        <CardHeader>
          <CardTitle><NuxtLink :to="`/groups/${group.slug}`" class="underline underline-offset-4">{{ group.name }}</NuxtLink></CardTitle>
          <CardDescription>{{ group.makeCount ?? 0 }} marcas · {{ group.modelYearCount ?? 0 }} modelos</CardDescription>
        </CardHeader>
        <CardContent>
          <NuxtLink :to="`/groups/${group.slug}`" class="text-sm font-medium underline underline-offset-4">Ver grupo</NuxtLink>
        </CardContent>
      </Card>
    </div>
    <Card v-else>
      <CardContent class="p-6 text-sm text-muted-foreground">No se encontraron grupos.</CardContent>
    </Card>
  </section>
</template>