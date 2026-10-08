<script setup lang="ts">
const isVisible = useCookie('carbase-beta-banner-visible', {
  default: () => true,
  maxAge: 60 * 60 * 24 * 365
})
</script>

<template>
  <div v-if="isVisible" role="status" class="border-b border-amber-500/30 bg-amber-500/10">
    <div class="mx-auto flex max-w-6xl items-center gap-3 px-4 py-2 text-sm">
      <Icon name="tabler:flask" class="size-4 shrink-0 text-amber-600 dark:text-amber-400" aria-hidden="true" />
      <p><span class="font-medium">CarBase está en fase beta.</span> Algunos datos o funciones pueden cambiar mientras mejoramos el catálogo.</p>
      <button
        type="button"
        class="ml-auto inline-flex size-8 shrink-0 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-amber-500/20 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        aria-label="Cerrar aviso de beta"
        title="Cerrar"
        @click="isVisible = false"
      >
        <Icon name="tabler:x" class="size-4" aria-hidden="true" />
      </button>
    </div>
  </div>
</template>
