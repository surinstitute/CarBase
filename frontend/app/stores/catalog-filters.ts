import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCatalogFiltersStore = defineStore('catalog-filters', () => {
  const search = ref('')
  const makeId = ref('all')
  const architecture = ref('all')

  function reset() {
    search.value = ''
    makeId.value = 'all'
    architecture.value = 'all'
  }

  return { search, makeId, architecture, reset }
})