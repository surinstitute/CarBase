import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCatalogFiltersStore = defineStore('catalog-filters', () => {
  const search = ref('')
  const makeId = ref('all')
  const modelName = ref('all')
  const year = ref('all')
  const assemblyCountry = ref('all')

  function reset() {
    search.value = ''
    makeId.value = 'all'
    modelName.value = 'all'
    year.value = 'all'
    assemblyCountry.value = 'all'
  }

  return { search, makeId, modelName, year, assemblyCountry, reset }
})