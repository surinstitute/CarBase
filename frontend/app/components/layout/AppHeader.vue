<script setup lang="ts">
import { Button } from '@/components/ui/button'

const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')

function toggleColorMode() {
  colorMode.preference = isDark.value ? 'light' : 'dark'
}
</script>

<template>
  <header class="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
    <div class="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
      <NuxtLink to="/" class="font-semibold tracking-tight">CarBase</NuxtLink>
      <nav aria-label="Navegación principal" class="flex items-center gap-2">
        <NuxtLink to="/models" class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground">Modelos</NuxtLink>
        <NuxtLink to="/makes" class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground">Marcas</NuxtLink>
        <NuxtLink to="/groups" class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground">Grupos</NuxtLink>
        <NuxtLink to="/recalls" class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground">Recalls</NuxtLink>
        <Button
          variant="outline"
          size="icon"
          aria-label="Alternar tema claro y oscuro"
          title="Alternar tema"
          @click="toggleColorMode"
        >
          <Icon name="tabler:contrast" aria-hidden="true" />
        </Button>
      </nav>
    </div>
  </header>
</template>