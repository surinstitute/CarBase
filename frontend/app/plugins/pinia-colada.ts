import { PiniaColada } from '@pinia/colada'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.$pinia.use(PiniaColada)
})