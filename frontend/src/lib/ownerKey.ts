const STORAGE_KEY = 'quote-vault:owner-key'

// The key itself is never part of the built app — it only ever exists in
// Render's env and, after a private one-time link, this browser's storage.
export function captureOwnerKeyFromUrl(): void {
  const params = new URLSearchParams(window.location.search)
  const key = params.get('key')
  if (!key) return

  try {
    localStorage.setItem(STORAGE_KEY, key)
  } catch {
    // storage unavailable — the request-time header just won't be sent
  }

  params.delete('key')
  const query = params.toString()
  window.history.replaceState(null, '', window.location.pathname + (query ? `?${query}` : ''))
}

export function getOwnerKey(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}
