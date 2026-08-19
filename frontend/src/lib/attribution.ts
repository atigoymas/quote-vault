const ATTRIBUTION_PATTERN = /\s+[—–-]\s+([^—–-]{2,80})$/

export function splitAttribution(raw: string): { text: string; author: string | null } {
  const match = raw.match(ATTRIBUTION_PATTERN)
  if (!match) return { text: raw, author: null }

  const author = match[1].trim()
  const text = raw.slice(0, match.index).trim()
  if (!text || !author) return { text: raw, author: null }

  return { text, author }
}
