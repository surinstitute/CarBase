<script setup lang="ts">
import { Button } from '@/components/ui/button'

const colorMode = useColorMode()
const route = useRoute()
const isDark = computed(() => colorMode.value === 'dark')
const isMenuOpen = ref(false)
const navigationLinks = [
  { label: 'Grupos', to: '/groups' },
  { label: 'Marcas', to: '/makes' },
  { label: 'Modelos', to: '/models' },
  { label: 'Vehículos', to: '/vehicles' },
  { label: 'Comparar', to: '/models/compare' },
  { label: 'Recalls', to: '/recalls' }
]

watch(() => route.fullPath, () => {
  isMenuOpen.value = false
})

function toggleColorMode() {
  colorMode.preference = isDark.value ? 'light' : 'dark'
}
</script>

<template>
  <header class="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
    <div class="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
      <NuxtLink to="/" class="font-semibold tracking-tight">CarBase</NuxtLink>
      <div class="ml-auto flex items-center gap-2">
        <nav aria-label="Navegación principal" class="hidden items-center gap-2 lg:flex">
          <NuxtLink v-for="link in navigationLinks" :key="link.to" :to="link.to" class="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground">{{ link.label }}</NuxtLink>
        </nav>
        <Button
          variant="outline"
          size="icon"
          aria-label="Alternar tema claro y oscuro"
          title="Alternar tema"
          @click="toggleColorMode"
        >
          <Icon name="tabler:contrast" aria-hidden="true" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          class="lg:hidden"
          :aria-label="isMenuOpen ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'"
          aria-controls="mobile-navigation"
          :aria-expanded="isMenuOpen"
          :title="isMenuOpen ? 'Cerrar menú' : 'Abrir menú'"
          @click="isMenuOpen = !isMenuOpen"
        >
          <Icon :name="isMenuOpen ? 'tabler:x' : 'tabler:menu-2'" aria-hidden="true" />
        </Button>
      </div>
    </div>
    <nav v-if="isMenuOpen" id="mobile-navigation" aria-label="Navegación principal" class="border-t px-4 py-2 lg:hidden">
      <NuxtLink
        v-for="link in navigationLinks"
        :key="link.to"
        :to="link.to"
        class="block rounded-md px-3 py-3 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
        @click="isMenuOpen = false"
      >
        {{ link.label }}
      </NuxtLink>
    </nav>
  </header>
</template>