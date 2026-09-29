import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCatalogFiltersStore = defineStore('catalog-filters', () => {
  const search = ref('')
  const makeId = ref('all')
  const year = ref('all')
  const bodyStyle = ref('all')
  const powertrainType = ref('all')
  const assemblyCountry = ref('all')

  function reset() {
    search.value = ''
    makeId.value = 'all'
    year.value = 'all'
    bodyStyle.value = 'all'
    powertrainType.value = 'all'
    assemblyCountry.value = 'all'
  }

  return { search, makeId, year, bodyStyle, powertrainType, assemblyCountry, reset }
})