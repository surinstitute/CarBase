export default defineEventHandler(async (event) => {
  const apiBase = useRuntimeConfig(event).djangoApiUrl.replace(/\/+$/, "");
  const query = getQuery(event);
  const params = new URLSearchParams();

  for (const name of ["q", "make", "body_style"]) {
    const value = query[name];
    if (typeof value === "string" && value.trim()) {
      params.set(name, value.trim());
    }
  }

  return $fetch<{ bodyStyles: string[] }>(
    `${apiBase}/models/filter-options/${params.size ? `?${params}` : ""}`,
  );
});
