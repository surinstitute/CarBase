// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/tailwind.css'],
  colorMode: {
    classSuffix: ''
  },
  runtimeConfig: {
    djangoApiUrl: 'http://localhost:8000/api'
  },

  modules: [
    '@nuxt/icon',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/image',
    '@nuxt/hints',
    '@pinia/nuxt',
    '@nuxtjs/color-mode',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/sitemap',
    '@nuxtjs/robots',
    '@nuxtjs/seo',
    'shadcn-nuxt'
  ],
  shadcn: {
    prefix: '',
    componentDir: '@/components/ui'
  }
})