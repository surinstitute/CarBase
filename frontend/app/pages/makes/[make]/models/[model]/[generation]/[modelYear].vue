<script setup lang="ts">
import ModelDetailPage from '../../../../../catalog/[id].vue'

const route = useRoute()
</script>

<template>
  <NuxtPage v-if="route.params.variantId" />
  <ModelDetailPage v-else />
</template>
