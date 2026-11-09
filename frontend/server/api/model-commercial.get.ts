import type { ApiPage, CommercialModel } from "#shared/types/catalog";
import { fetchAllPages } from "../utils/django";

export default defineEventHandler(async (event): Promise<ApiPage<CommercialModel>> => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, "");
  const query = getQuery(event);
  const params = new URLSearchParams();

  for (const name of ["q", "make", "name", "page"]) {
    const value = query[name];
    if (typeof value === "string" && value.trim()) {
      params.set(name, value.trim());
    }
  }

  const url = `${apiBase}/model-commercial/${params.size ? `?${params}` : ""}`;
  return params.has("page")
    ? $fetch<ApiPage<CommercialModel>>(url)
    : fetchAllPages<CommercialModel>(url);
});
