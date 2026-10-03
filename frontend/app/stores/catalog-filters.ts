import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCatalogFiltersStore = defineStore('catalog-filters', () => {
  const search = ref('')
  const makeId = ref('all')
  const bodyStyle = ref('all')

  function reset() {
    search.value = ''
    makeId.value = 'all'
    bodyStyle.value = 'all'
  }

  return { search, makeId, bodyStyle, reset }
})