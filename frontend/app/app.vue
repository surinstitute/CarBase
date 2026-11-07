<template>
  <div class="flex min-h-screen flex-col">
    <LayoutBetaBanner />
    <LayoutAppHeader />
    <main
      class="flex-1"
      :class="{ 'flex flex-col': $route.path === '/vehicles' }"
    >
      <NuxtPage />
    </main>
    <CatalogCompareBar />
    <LayoutAppFooter />
  </div>
</template>
