document.addEventListener("change", (event) => {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || !input.name.endsWith("-image_file")) {
    return;
  }

  const preview = input.closest(".form-row")?.querySelector(".image-placement-preview");
  if (!preview) {
    return;
  }

  if (preview.dataset.objectUrl) {
    URL.revokeObjectURL(preview.dataset.objectUrl);
    delete preview.dataset.objectUrl;
  }

  const file = input.files?.[0];
  if (!file) {
    const originalSource = preview.dataset.originalSrc;
    preview.hidden = !originalSource;
    if (originalSource) {
      preview.src = originalSource;
    } else {
      preview.removeAttribute("src");
    }
    return;
  }

  const objectUrl = URL.createObjectURL(file);
  preview.dataset.objectUrl = objectUrl;
  preview.src = objectUrl;
  preview.alt = file.name;
  preview.hidden = false;
});