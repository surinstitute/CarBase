<script setup lang="ts">
import VehiclesSearchPage from './vehicles/index.vue'

useSeoMeta({
  title: 'Buscar vehículos',
  description: 'Busca marcas, modelos y versiones de vehículos.'
})
</script>

<template>
  <VehiclesSearchPage />
</template>