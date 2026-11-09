import type { CatalogCollectionDetail } from "#shared/types/catalog";

export default defineEventHandler(async (event) => {
  const slug = getRouterParam(event, "slug");
  if (!slug) {
    throw createError({
      statusCode: 400,
      statusMessage: "Collection slug is required",
    });
  }

  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, "");
  return $fetch<CatalogCollectionDetail>(
    `${apiBase}/collections/${encodeURIComponent(slug)}/`,
  );
});
