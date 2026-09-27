import { hydrateQueryCache, PiniaColada, serializeQueryCache, useQueryCache } from '@pinia/colada'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PiniaColada)
  const queryCache = useQueryCache(nuxtApp.$pinia)
  const payloadKey = 'pinia-colada-cache'

  if (import.meta.server) {
    nuxtApp.hook('app:rendered', () => {
      nuxtApp.payload.data[payloadKey] = serializeQueryCache(queryCache)
    })
  } else {
    const serializedCache = nuxtApp.payload.data[payloadKey]
    if (serializedCache) {
      hydrateQueryCache(queryCache, serializedCache)
    }
  }
})