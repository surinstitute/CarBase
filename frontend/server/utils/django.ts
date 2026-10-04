import type { ApiPage } from '#shared/types/catalog'

export async function fetchAllPages<T>(url: string): Promise<ApiPage<T>> {
  const firstPage = await $fetch<ApiPage<T>>(url)
  const results = [...firstPage.results]
  let nextPage = firstPage.next

  while (nextPage) {
    const page = await $fetch<ApiPage<T>>(nextPage)
    results.push(...page.results)
    nextPage = page.next
  }

  return {
    count: firstPage.count,
    next: null,
    previous: null,
    results
  }
}
