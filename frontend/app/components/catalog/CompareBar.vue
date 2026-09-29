<script setup lang="ts">
import { Button } from '@/components/ui/button'

const comparison = useCarComparison()
</script>

<template>
  <aside
    v-if="comparison.count.value"
    class="fixed inset-x-0 bottom-0 z-20 border-t bg-background/95 px-4 py-3 shadow-lg backdrop-blur"
    aria-label="Autos seleccionados para comparar"
  >
    <div class="mx-auto flex max-w-6xl items-center justify-between gap-3">
      <div class="min-w-0">
        <p class="text-sm font-semibold">{{ comparison.count.value }} de 4 autos seleccionados</p>
        <p class="hidden truncate text-xs text-muted-foreground sm:block">
          {{ comparison.selectedVehicles.value.map((vehicle) => `${vehicle.makeName} ${vehicle.modelName} ${vehicle.variantName || ''}`).join(' · ') }}
        </p>
      </div>
      <div class="flex shrink-0 items-center gap-2">
        <Button type="button" variant="ghost" size="sm" @click="comparison.clear()">
          Limpiar
        </Button>
        <Button v-if="comparison.canCompare.value" as-child size="sm">
          <NuxtLink to="/models/compare">
            <Icon name="tabler:scale" class="size-4" aria-hidden="true" />
            Comparar
          </NuxtLink>
        </Button>
        <span v-else class="text-xs text-muted-foreground">Añade otro para comparar</span>
      </div>
    </div>
  </aside>
</template>