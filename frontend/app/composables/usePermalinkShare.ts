type PermalinkShareStatus = 'idle' | 'shared' | 'copied' | 'error'

export function usePermalinkShare() {
  const status = ref<PermalinkShareStatus>('idle')

  async function sharePermalink(path: string, title: string) {
    const url = new URL(path, window.location.origin).toString()

    if (navigator.share) {
      try {
        await navigator.share({ title, url })
        status.value = 'shared'
        return
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          status.value = 'idle'
          return
        }
      }
    }

    try {
      await navigator.clipboard.writeText(url)
      status.value = 'copied'
    } catch {
      status.value = 'error'
    }
  }

  return { sharePermalink, status }
}
