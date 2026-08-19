const STORAGE_KEY = 'quote-vault:owner-key'

// The key itself is never part of the built app or any URL — it only ever
// exists in Render's env and, once entered here, this browser's storage.
export function setOwnerKey(key: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, key)
  } catch {
    // storage unavailable — the request-time header just won't be sent
  }
}

export function getOwnerKey(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}
