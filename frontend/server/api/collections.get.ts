import type { CatalogCollection } from "#shared/types/catalog";
import { fetchAllPages } from "../utils/django";

export default defineEventHandler(async (event) => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, "");
  return fetchAllPages<CatalogCollection>(`${apiBase}/collections/`);
});
